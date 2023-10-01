import datetime
import logging
from datetime import timedelta

import pyodbc
from odoo import SUPERUSER_ID
from odoo import api
from odoo import models, fields, _

_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError

driver = '{ODBC Driver 17 for SQL Server}'
IN_CODE = 'IN'
OUT_CODE = 'OUT'
RFID_IN_CODE = 'IN_RFID'
VALID_DATA = "Valid"

MAX_ATTEMPT_TO_SUCCESS = 5

get_BADGENUMBER = """SELECT DISTINCT (%s)
                     FROM %s 
                     WHERE IsRead = 0"""

get_employee_ids = """SELECT employee_device_id, id
                      FROM hr_employee WHERE employee_device_id IN %s"""

update_device_attendance = """UPDATE %s SET IsRead = 1 WHERE IsRead = 0 AND id IN %s"""

get_att_data_sql = """SELECT
                          att.emp_code, att.terminal_alias, att.punch_time, att.id
                      FROM %s att                      
                      WHERE att.IsRead = 0 AND att.id <= ?
                      ORDER BY att.emp_code, att.punch_time ASC"""


class DeviceDetail(models.Model):
    _name = 'hr.attendance.device.detail'
    _description = "Device Detail"

    name = fields.Char(size=100, string='Location', required='True')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required='True')
    is_active = fields.Boolean(string='Is Active', default=False)
    connection_type = fields.Selection([
        ('ip', "IP"),
        ('url', "URL"),
        ('port', "Port")
    ], string='Connection Type', required=True)
    device_brand = fields.Selection(string="Device Brand", selection=[],
                                    help="Allows you to define which brand you would like to connect")

    server = fields.Char(size=100, string='Server Address')
    database = fields.Char(size=100, string='Database Name')

    username = fields.Char(size=100, string='Username')
    password = fields.Char(size=100, string='Password')
    db_table = fields.Char(size=50, string='Table Name')

    last_update = fields.Datetime(string='Update On(Pull)')
    duty_date_set_last_update = fields.Datetime(string='Updated On(Duty Date)')

    """ Relational Fields """
    attendance_table_fields = fields.One2many('attendance.table.field', 'device_detail_id', string='Devices')
    device_lines = fields.One2many('hr.attendance.device.line', 'device_detail_id', string='Devices')
    device_line_details = fields.One2many('hr.attendance.device.line.details', 'device_line_id', string='Device Lines')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Location is already in use'),
        ('code_uniq', 'unique(device_code)', 'This Code is already in use'),
    ]

    def toggle_connect(self):
        self.is_active = not self.is_active

    def action_pull_error_data(self):

        attendanceErrorProcess = self.env['hr.attendance.error.data.temp']
        attendanceErrorProcess.doErrorToSuccess()

    def action_set_duty_date(self):
        self.ensure_one()
        attendanceErrorProcess = self.env['hr.attendance.error.data.temp']
        attendanceErrorProcess.setDutyDate(self.operating_unit_id.id)
        self.sudo().duty_date_set_last_update = datetime.datetime.now()

    def action_check_connection(self):

        isConnect = False
        conn = None
        cursor = None
        is_rigth_url = False
        try:

            is_rigth_url = True
            # _logger.info(driver)
            conn = pyodbc.connect('DRIVER=' + driver + ';PORT=1433;SERVER=' +
                                  self.server + ';DATABASE=' +
                                  self.database + ';UID=' + self.username +
                                  ';PWD=' + self.password)
            cursor = conn.cursor()
            isConnect = True
        except Exception as e:
            error_message = "Error: Unable to pull data." + "\n Check Connection: " + "  \n Error Message : " + str(e)
            _logger.error(error_message)
            isConnect = False
        finally:
            # if cursor is not None:
            #     cursor.close()
            # if conn is not None:
            #     conn.close()
            if isConnect:
                view = self.env.ref('sh_message.sh_message_wizard')
                view_id = view and view.id or False
                context = dict(self._context or {})
                context['message'] = "Successfully connect to the " + self.name + " (" + self.server + ") server."
                return {
                    'name': 'Success',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sh.message.wizard',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'context': context
                }

                # raise Warning("Successfully connect to the "+self.name+" ("+self.server+ ") server.")
            else:
                if not is_rigth_url:
                    raise ValidationError(
                        'You can not pull date from this server, please check "Server Base URL" or contact admin.')
                else:
                    raise ValidationError(
                        "Unable to connect the " + self.server + " server. Please check the configuration.")

    @api.model
    def send_email_notification(self):

        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template_id = self.env['ir.model.data'].get_object_reference('pdcl_hr_device_config',
                                                                     'email_notification_template')[1]
        template_browse = self.env['mail.template'].browse(template_id)

        if template_browse:
            grp = self.env['res.groups'].search([('full_name', '=', "Attendance/Manager")], limit=1)
            for user in grp.users:
                values = template_browse.generate_email(user.id, fields=None)
                values['subject'] = values['subject'] + " " + str(datetime.date.today())
                values['email_to'] = user.email
                values['email_from'] = su_id.email
                values['res_id'] = False
                if not values['email_to'] and not values['email_from']:
                    pass
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    mail_mail_obj.send(msg_id)

    @api.model
    def pull_automation(self):
        # _logger.info "Calling pull_automation()"
        for dc in self.search([('is_active', '=', True)]):
            try:
                dc.action_pull_data(True)
                self.env.cr.commit()
                dc.action_set_duty_date()
                # self.send_email_notification()
            except Exception as e:
                self.env.cr.commit()
                _logger.error(e[0])
                pass
            finally:
                self.env.cr.commit()

    def compare_base_url_with_current_url(self):
        base_url = self.getBaseURL()
        current_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url == current_url:
            return True
        else:
            return False

    def action_pull_data(self, IsScheduler=False):
        _logger.info("Calling action_pull_data()")

        db_table = self.db_table or False
        error_message = ""
        success_message = ""
        isConnect = False
        conn = None
        cursor = None
        is_right_url = self.compare_base_url_with_current_url()

        if not is_right_url:
            if not IsScheduler:
                msg = 'Please contact your administrator.'

                raise ValidationError(msg)

        try:
            hr_att_device_pool = self.env['hr.attendance.device.detail']
            attDevice = hr_att_device_pool.search([('id', '=', self.id)])
            if attDevice is None:
                _logger.error("Unable to get device. ID:" + self.id)
                error_message = "Unable to get device. ID:" + self.id
                return

            conn = pyodbc.connect('DRIVER=' + driver + ';PORT=1433;SERVER=' +
                                  self.server + ';DATABASE=' +
                                  self.database + ';UID=' + self.username +
                                  ';PWD=' + self.password)
            cursor = conn.cursor()
            isConnect = True

            currentDate = datetime.datetime.now()

            error_message = self.processData(attDevice, conn, cursor)

            if error_message is None or len(error_message) == 0:
                self.sudo().write({'last_update': currentDate})
                success_message = "Successfully pull the data from " + self.name + " (" + self.server + ") server."
                # _logger.info("Attendance Date pull from " + attDevice.server + " : at " + str(
                #     datetime.datetime.now()) + " Whrere checkoutin table ID between: " + str(minId[0]) + "to" + str(
                #     maxId[0]))

        except Exception as e:

            _logger.error(e)
            error_message = e

        finally:
            # if cursor is not None:
            #     cursor.close()
            # if conn is not None:
            #     conn.close()
            if isConnect == False:
                if is_right_url == False:
                    # _logger.info "Error Line# 202"
                    msg = "Attendance only pull from a specific server. Please check attendance settings or contact administrator."
                    if not IsScheduler:
                        raise ValidationError(msg)
                    else:
                        _logger.error(msg)
                else:
                    msg = "Unable to connect the " + self.server + " server. Please check the configuration."
                    if not IsScheduler:
                        raise ValidationError(msg)
                    else:
                        _logger.error(msg)
            elif error_message is not None and len(str(error_message)) > 0:
                if not IsScheduler:
                    raise ValidationError(error_message)
                else:
                    _logger.error(error_message)
            else:
                if not IsScheduler:
                    res = self.env.ref('attendance_connector_mssql.success_msg_wizard_id')
                    result = {
                        'name': _('Success Message'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'view_id': res and res.id or False,
                        'res_model': 'success.msg.wizard',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'new',
                    }
                    return result

    def is_live_server(self, app_url):
        return True

    def getBaseURL(self):

        query = """SELECT 
                         server_url
                    FROM
                         res_config_settings 
                    order by id desc limit 1"""

        self._cr.execute(query, (tuple([])))
        server_url = self._cr.fetchone()

        if server_url[0] == None:
            return ""

        return server_url[0].strip()

    def mapping_employee_ids(self, cursor, employee_code, db_table):
        employeeIdMap = {}

        sql_query = get_BADGENUMBER % (employee_code, db_table)
        cursor.execute(sql_query)
        badge_numbers = cursor.fetchall()
        _logger.info(badge_numbers)

        if badge_numbers is None:
            return

        badge_numbers_lst = []
        for item in badge_numbers:
            badge_numbers_lst.append(item[0])

        employee_device_id = self.env['hr.employee'].search(['|', ('active', '=', True),
                                                             ('active', '=', False)]).read(['employee_device_id'])
        # Where key is employee_device_id
        for i in employee_device_id:
            if (str(i.get('employee_device_id')) in badge_numbers_lst):
                employeeIdMap[str(i.get('employee_device_id'))] = i.get('id')
            elif (str(int(i.get('employee_device_id'))) in badge_numbers_lst):
                employeeIdMap[str(int(i.get('employee_device_id')))] = i.get('id')
            else:
                _logger.info(f"Not found {i.get('id')}")

        return employeeIdMap

    def processData(self, attDevice, conn, cursor):
        return ""

    def isValidByDuration(self, currentRow, previousRow, deviceInOutCode, tolerableSecond):

        # usr.BADGENUMBER, att.VERIFYCODE, att.CHECKTIME, att.SENSORID

        if len(previousRow) == 0:
            return True

        # Check same Employee or not
        if currentRow[0] != previousRow[0]:
            return True

        if deviceInOutCode:

            currentType = ""
            previousType = ""

            # Get same attendance type or not

            if (deviceInOutCode.get(str(currentRow[2])) == IN_CODE or deviceInOutCode.get(
                    str(currentRow[2])) == RFID_IN_CODE):
                currentType = IN_CODE
            elif deviceInOutCode.get(str(currentRow[2])) == OUT_CODE:
                currentType = OUT_CODE

            if (deviceInOutCode.get(str(previousRow[2])) == IN_CODE or deviceInOutCode.get(
                    str(previousRow[2])) == RFID_IN_CODE):
                previousType = IN_CODE
            elif deviceInOutCode.get(str(previousRow[2])) == OUT_CODE:
                previousType = OUT_CODE

            # Check same attendance type or not
            if currentType != previousType:
                return True

        # Check tolerable duration
        durationInSecond = (currentRow[1] - previousRow[1]).total_seconds()
        if durationInSecond > tolerableSecond:
            return True
        else:
            return False

    def storeData(self, row, deviceInOutCode, employeeIdMap, operatingUnitId):
        return None, None

    def createData(self, row, employeeId, inOrOut, hr_att_pool, operatingUnitId):
        res = None
        try:
            if inOrOut == IN_CODE:
                create_vals = {'employee_id': employeeId,
                               'check_in': self.convertDateTime(row[1]),
                               'create_date': datetime.datetime.now(),
                               'write_date': datetime.datetime.now(),
                               'has_error': True,
                               # 'manual_attendance_request': False,
                               'is_system_generated': True,
                               'operating_unit_id': operatingUnitId.id}
            else:
                create_vals = {'employee_id': employeeId,
                               'check_in': None,
                               'check_out': self.convertDateTime(row[1]),
                               'create_date': datetime.datetime.now(),
                               'write_date': datetime.datetime.now(),
                               'has_error': True,
                               # 'manual_attendance_request': False,
                               'is_system_generated': True,
                               'operating_unit_id': operatingUnitId.id}
            res = hr_att_pool.create(create_vals)
            return "", res
        except Exception as e:
            self.env.cr.rollback()
            error_message = "Error: Unable to process data." + "\n createData: " + str(
                row) + "  \n Error Message : " + str(e)
            _logger.error(error_message)
            return error_message, res

    def saveAsError(self, row, employeeIdMap, deviceInOutCode, operatingUnitId, reason):

        attendance_error_obj = self.env['hr.attendance.import.error']
        _logger.info(reason)
        _logger.info(row)

        error_vals = {}
        if (deviceInOutCode.get(str(row[1])) == IN_CODE or deviceInOutCode.get(str(row[1])) == RFID_IN_CODE):
            error_vals['check_in'] = self.convertDateTime(row[2])
        else:
            error_vals['check_out'] = self.convertDateTime(row[2])

        if employeeIdMap.get(row[0]) is not None:
            error_vals['employee_id'] = employeeIdMap.get(row[0])
        else:
            error_vals['employee_code'] = row[0]

        error_vals['operating_unit_id'] = operatingUnitId
        error_vals['reason'] = reason

        attendance_error_obj.create(error_vals)
        return ""

    def isValidData(self, row, deviceInOutCode, employeeIdMap):
        # _logger.info(row)
        if row[0] is None:  # Check employee_device_id is not null
            return "Empty Acc No"
        if employeeIdMap.get(str(row[0])) is None:  # Check employee_device_id is mapped or not
            return "Unmapped Emp Acc"
        if row[2] is None:  # Check in_out code is not null
            return "Empty Code"
        if deviceInOutCode.get(str(row[2])) != IN_CODE and deviceInOutCode.get(
                str(row[2])) != RFID_IN_CODE and deviceInOutCode.get(
            str(row[2])) != OUT_CODE:  # Check in_out code is valid or not
            return "Unmapped Code"
        if row[1] is None:  # Check time is not null
            return "Empty Check Time"
        # if row[3] is None: # Check sensor_id is not null
        #     return "Empty Sensor ID"
        return VALID_DATA

    def getDateTimeFromStr(self, dateStr, dtFormat="%Y-%m-%d %H:%M:%S"):
        if dateStr:
            return datetime.datetime.strptime(dateStr, dtFormat)
        else:
            return None

    def convertDateTime(self, dateStr):
        if dateStr:
            return dateStr + timedelta(hours=-6)

    def getAttDeviceRulesRule(self):

        query = """SELECT 
                         time_duration
                    FROM
                         res_config_settings
                    order by id desc limit 1"""

        self._cr.execute(query, (tuple([])))
        deduction_rule_value = self._cr.fetchone()

        if not deduction_rule_value:
            return 0

        return deduction_rule_value[0]
