from odoo import models, fields, _
from odoo import api
from odoo.http import request
import pyodbc
import datetime
from datetime import timedelta
from odoo import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

from odoo.exceptions import Warning, ValidationError
from odoo import http

driver = '{ODBC Driver 17 for SQL Server}'
IN_CODE = 'IN'
OUT_CODE = 'OUT'
RFID_IN_CODE = 'IN_RFID'
VALID_DATA = "Valid"

MAX_ATTEMPT_TO_SUCCESS = 5

get_BADGENUMBER = """SELECT DISTINCT (USERID)
                     FROM CheckInOuts 
                     WHERE IsRead = 0 AND Id <= ?"""

get_employee_ids = """SELECT device_employee_acc, id
                      FROM hr_employee WHERE device_employee_acc IN %s"""

get_att_data_sql = """SELECT
                          att.USERID, att.CheckType, att.CHECKTIME, att.SENSORID
                      FROM CHECKINOUTS att                      
                      WHERE att.IsRead = 0 AND att.Id <= ?
                      ORDER BY att.USERID, att.CHECKTIME ASC"""


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

    server = fields.Char(size=100, string='Server Address')
    database = fields.Char(size=100, string='Database Name')

    username = fields.Char(size=100, string='Username')
    password = fields.Char(size=100, string='Password')

    last_update = fields.Datetime(string='Update On(Pull)')
    duty_date_set_last_update = fields.Datetime(string='Updated On(Duty Date)')

    """ Relational Fields """
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
            # print(driver)
            conn = pyodbc.connect('DRIVER=' + driver + ';PORT=1433;SERVER=' +
                                  self.server + ';DATABASE=' +
                                  self.database + ';UID=' + self.username +
                                  ';PWD=' + self.password)
            cursor = conn.cursor()
            isConnect = True
        except Exception as e:
            error_message = "Error: Unable to pull data." + "\n Check Connection: " + "  \n Error Message : " + reason
            _logger.error(error_message)
            isConnect = False
        finally:
            # if cursor is not None:
            #     cursor.close()
            # if conn is not None:
            #     conn.close()
            if isConnect == True:
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
                if is_rigth_url == False:
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
        # print "Calling pull_automation()"
        for dc in self.search([]):
            try:
                dc.action_pull_data()
                self.env.cr.commit()
                dc.action_set_duty_date()
                # self.send_email_notification()
            except Exception as e:
                self.env.cr.commit()
                _logger.error(e[0])
                pass
            finally:
                self.env.cr.commit()

    def action_pull_data(self):
        print("Calling action_pull_data()")

        error_message = ""
        success_message = ""
        isConnect = False
        conn = None
        cursor = None
        is_rigth_url = False
        try:

            is_rigth_url = True
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
            cursor.execute("""SELECT max(Id) FROM CHECKINOUTS WHERE IsRead = 0""")
            maxId = cursor.fetchone()
            print("maxID:", maxId)

            cursor.execute("""SELECT min(Id) FROM CHECKINOUTS WHERE IsRead = 0""")
            minId = cursor.fetchone()

            if maxId[0] is None:
                success_message = "Attendance data are already updated. There are no new attendance data yet."
                return

            error_message = self.processData(maxId[0], attDevice, conn, cursor)

            if len(error_message) == 0:
                self.sudo().write({'last_update': currentDate})
                success_message = "Successfully pull the data from " + self.name + " (" + self.server + ") server."
                _logger.info("Attendance Date pull from " + attDevice.server + " : at " + str(
                    datetime.datetime.now()) + " Whrere checkoutin table ID between: " + str(minId[0]) + "to" + str(
                    maxId[0]))

        except Exception as e:

            _logger.error(e)
            error_message = e

        finally:
            # if cursor is not None:
            #     cursor.close()
            # if conn is not None:
            #     conn.close()
            if isConnect == False:
                if is_rigth_url == False:
                    # print "Error Line# 202"
                    raise ValidationError(
                        "Attendance only pull from a specific server. Please check attendance settings or contact administrator.")
                else:
                    raise ValidationError(
                        "Unable to connect the " + self.server + " server. Please check the configuration.")
            elif len(str(error_message)) > 0:
                raise ValidationError(error_message)
            else:
                res = self.env.ref('pdcl_hr_device_config.success_msg_wizard_id')
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

    def processData(self, maxId, attDevice, conn, cursor):
        print("Calling processData()")

        deviceInOutCode = {}  # Where key is code and value is "IN" OR OUT

        tolerableSecond = self.getAttDeviceRulesRule()
        if tolerableSecond == 0:
            tolerableSecond = 300

        for line_detail in attDevice.device_line_details:
            if line_detail.type_code == IN_CODE:
                deviceInOutCode[str(line_detail.type_value)] = IN_CODE
            elif line_detail.type_code == RFID_IN_CODE:
                deviceInOutCode[str(line_detail.type_value)] = IN_CODE
            elif line_detail.type_code == OUT_CODE:
                deviceInOutCode[str(line_detail.type_value)] = OUT_CODE

        # Map employee_id to device_employee_acc
        cursor.execute(get_BADGENUMBER, maxId)
        badge_numbers = cursor.fetchall()
        print(badge_numbers)

        if badge_numbers is None:
            return

        badge_numbers_lst = []
        for item in badge_numbers:
            badge_numbers_lst.append(item[0])

        self._cr.execute(get_employee_ids, (tuple(badge_numbers_lst),))
        employee_ids = self._cr.fetchall()

        employeeIdMap = {}  # Where key is device_employee_acc
        for item in employee_ids:
            employeeIdMap[str(item[0])] = item[1]
        _logger.info("EmployeeIdMap Data:" + str(employeeIdMap))

        cursor.execute(get_att_data_sql, maxId)
        att_rows = cursor.fetchall()
        _logger.info(
            "Attendance Date pull from " + attDevice.server + " : at " + str(datetime.datetime.now()) + " : " + str(
                att_rows))

        try:
            previousRow = {}
            for row in att_rows:
                reason = ""
                reason = self.isValidData(row, deviceInOutCode, employeeIdMap)
                if reason != VALID_DATA:
                    reason = self.saveAsError(row, employeeIdMap, deviceInOutCode, attDevice.operating_unit_id, reason)
                else:
                    if self.isValidByDuration(row, previousRow, deviceInOutCode, tolerableSecond) == True:
                        reason = self.storeData(row, deviceInOutCode, employeeIdMap, attDevice.operating_unit_id)
                    previousRow = row

            # Store all attendance data to application database.
            # Now Update on SQL Server Database(External)
            cursor.execute("UPDATE CHECKINOUTS SET IsRead = 1 WHERE id <=? AND IsRead = 0", maxId)
            conn.commit()

            return reason

        except Exception as e:
            self.env.cr.rollback()
            error_message = "Error: Unable to pull data." + "\n Attendance Data: " + str(
                row) + "  \n Error Message : " + str(e)
            _logger.error(error_message)
            return error_message

    def isValidByDuration(self, currentRow, previousRow, deviceInOutCode, tolerableSecond):

        # usr.BADGENUMBER, att.VERIFYCODE, att.CHECKTIME, att.SENSORID

        if len(previousRow) == 0:
            return True

        # Check same Employee or not
        if currentRow[0] != previousRow[0]:
            return True

        currentType = ""
        previousType = ""

        # Get same attendance type or not

        if (deviceInOutCode.get(str(currentRow[1])) == IN_CODE or deviceInOutCode.get(
                str(currentRow[1])) == RFID_IN_CODE):
            currentType = IN_CODE
        elif deviceInOutCode.get(str(currentRow[1])) == OUT_CODE:
            currentType = OUT_CODE

        if (deviceInOutCode.get(str(previousRow[1])) == IN_CODE or deviceInOutCode.get(
                str(previousRow[1])) == RFID_IN_CODE):
            previousType = IN_CODE
        elif deviceInOutCode.get(str(previousRow[1])) == OUT_CODE:
            previousType = OUT_CODE

        # Check same attendance type or not
        if currentType != previousType:
            return True

        # Check tolerable duration
        durationInSecond = (currentRow[2] - previousRow[2]).total_seconds()
        if durationInSecond > tolerableSecond:
            return True
        else:
            return False

    def storeData(self, row, deviceInOutCode, employeeIdMap, operatingUnitId):
        try:
            res = ""
            hr_att_pool = self.env['hr.attendance']

            employeeId = employeeIdMap.get(str(row[0]))

            if (deviceInOutCode.get(str(row[1])) == IN_CODE or deviceInOutCode.get(str(row[1])) == RFID_IN_CODE):
                res = self.createData(row, employeeId, IN_CODE, hr_att_pool, operatingUnitId)

            elif deviceInOutCode.get(str(row[1])) == OUT_CODE:

                preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                                 ('check_in', '!=', False)], limit=1, order='check_in desc')

                # preAttData = hr_att_pool.search([('employee_id', '=', employeeId)], limit=1,
                #                                                   order='check_in desc')

                if preAttData and preAttData.check_out is False:
                    # chk_in = self.getDateTimeFromStr(preAttData.check_in)
                    chk_in = preAttData.check_in
                    durationInHour = (self.convertDateTime(row[2]) - chk_in).total_seconds() / 60 / 60
                    if durationInHour <= 15 and durationInHour >= 0:
                        preAttData.write({'check_out': self.convertDateTime(row[2]),
                                          'worked_hours': durationInHour,
                                          'write_date': datetime.datetime.now(),
                                          'has_error': False,
                                          'operating_unit_id': operatingUnitId
                                          })
                    else:
                        res = self.createData(row, employeeId, OUT_CODE, hr_att_pool, operatingUnitId)
                else:
                    res = self.createData(row, employeeId, OUT_CODE, hr_att_pool, operatingUnitId)
            return res
        except Exception as e:
            self.env.cr.rollback()
            error_message = "Error: Unable to pull data." + "\n Attendance Data: " + "\n storeData: " + str(
                row) + "  \n Error Message : " + str(e)
            _logger.error(error_message)
            return error_message

    def createData(self, row, employeeId, inOrOut, hr_att_pool, operatingUnitId):
        try:
            if inOrOut == IN_CODE:
                create_vals = {'employee_id': employeeId,
                               'check_in': self.convertDateTime(row[2]),
                               'create_date': datetime.datetime.now(),
                               'write_date': datetime.datetime.now(),
                               'has_error': True,
                               # 'manual_attendance_request': False,
                               'is_system_generated': True,
                               'operating_unit_id': operatingUnitId}
            else:
                create_vals = {'employee_id': employeeId,
                               'check_in': None,
                               'check_out': self.convertDateTime(row[2]),
                               'create_date': datetime.datetime.now(),
                               'write_date': datetime.datetime.now(),
                               'has_error': True,
                               # 'manual_attendance_request': False,
                               'is_system_generated': True,
                               'operating_unit_id': operatingUnitId}
            hr_att_pool.create(create_vals)
            return ""
        except Exception as e:
            self.env.cr.rollback()
            error_message = "Error: Unable to pull data." + "\n Attendance Data: " + "\n storeData: " + str(
                row) + "  \n Error Message : " + str(e)
            _logger.error(error_message)
            return error_message

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
        print(row)
        if row[0] is None:  # Check device_employee_acc is not null
            return "Empty Acc No"
        if employeeIdMap.get(str(row[0])) is None:  # Check device_employee_acc is mapped or not
            return "Unmapped Emp Acc"
        if row[1] is None:  # Check in_out code is not null
            return "Empty Code"
        if deviceInOutCode.get(str(row[1])) != IN_CODE and deviceInOutCode.get(
                str(row[1])) != RFID_IN_CODE and deviceInOutCode.get(
                str(row[1])) != OUT_CODE:  # Check in_out code is valid or not
            return "Unmapped Code"
        if row[2] is None:  # Check time is not null
            return "Empty Check Time"
        # if row[3] is None: # Check sensor_id is not null
        #     return "Empty Sensor ID"
        return VALID_DATA

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
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