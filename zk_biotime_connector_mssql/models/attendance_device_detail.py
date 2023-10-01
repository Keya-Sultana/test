import logging
import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

IN_CODE = 'IN'
OUT_CODE = 'OUT'
RFID_IN_CODE = 'IN_RFID'
VALID_DATA = "Valid"

get_att_data_sql = """SELECT
                          att.emp_code, att.punch_time, att.terminal_alias, att.id
                      FROM %s att                      
                      WHERE att.IsRead = 0 AND att.id <= ?
                      ORDER BY att.emp_code, att.punch_time ASC"""


class AttendanceDeviceDetail(models.Model):
    _inherit = 'hr.attendance.device.detail'

    device_brand = fields.Selection(selection_add=[('zk_biotime', 'ZK Biotime')])

    def processData(self, attDevice, conn, cursor):
        res = super().processData(attDevice, conn, cursor)

        if attDevice.device_brand == 'zk_biotime':

            _logger.info("Calling processData(zk_biotime)")
            db_table = attDevice.db_table or False
            for f in attDevice.attendance_table_fields:
                if f.type_code == 'employee_code':
                    employee_code = f.type_value
                elif f.type_code == 'att_date':
                    att_date = f.type_value
                elif f.type_code == 'att_time':
                    att_time = f.type_value
                elif f.type_code == 'att_date_time':
                    att_date_time = f.type_value
                elif f.type_code == 'IN_OUT':
                    IN_OUT = f.type_value

            sql_query = "SELECT max(Id) FROM %s WHERE IsRead = 0" % db_table
            cursor.execute(sql_query)
            maxId = cursor.fetchone()

            sql_query = "SELECT min(Id) FROM %s WHERE IsRead = 0" % db_table
            cursor.execute(sql_query)
            minId = cursor.fetchone()

            if maxId[0] is None:
                return

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

            # Map employee_id to employee_device_id
            employeeIdMap = attDevice.mapping_employee_ids(cursor, employee_code, db_table)

            sql_query = get_att_data_sql % db_table
            cursor.execute(sql_query, maxId)
            att_rows = cursor.fetchall()

            process_records = []
            reason = ""

            try:
                previousRow = {}

                for row in att_rows:
                    _logger.info(row)
                    machine_att = self.env['machine.attendance'].search([('employee_code', '=', row[0]),
                                                                         ('punching_time', '=', row[1])], limit=1)
                    if not machine_att:
                        machine_att = self.env['machine.attendance'].create({
                            'employee_code': row[0],
                            'punching_time': row[1],
                            'employee_id': employeeIdMap.get(str(row[0])) or False,
                            'operating_unit_id': attDevice.operating_unit_id.id,
                            'device_id': attDevice.id
                        })
                    reason = ""
                    reason = self.isValidData(row, deviceInOutCode, employeeIdMap)
                    if reason != VALID_DATA:
                        if reason != "Unmapped Emp Acc":
                            raise ValidationError(reason)
                        else:
                            reason = None
                    else:
                        if self.isValidByDuration(row, previousRow, deviceInOutCode, tolerableSecond):
                            reason, att_rec = self.storeData(row, deviceInOutCode, employeeIdMap,
                                                             attDevice.operating_unit_id)
                        previousRow = row
                        process_records.append(row[3])
                        vals = {'state': '1'}
                        if att_rec is not None:
                            vals['attendance_id'] = att_rec.id
                        machine_att.write(vals)

                # Store all attendance data to application database.
                # Now Update on SQL Server Database(External)

                sql_query = "UPDATE %s SET IsRead = 1 WHERE id <=? AND IsRead = 0" % db_table
                # cursor.execute("UPDATE iclock_transaction SET IsRead = 1 WHERE id <=? AND IsRead = 0", maxId)
                cursor.execute(sql_query, maxId)
                conn.commit()

                return reason

            except Exception as e:
                if process_records:
                    sql_query = "UPDATE %s SET IsRead = 1 WHERE IsRead = 0 AND id in {}" % db_table
                    # cursor.execute("UPDATE iclock_transaction SET IsRead = 1 WHERE IsRead = 0 AND id in {}".format(
                    #     tuple(process_records)))
                    cursor.execute(sql_query.format(tuple(process_records)))
                    conn.commit()
                    self.env.cr.commit()
                error_message = "Error: Unable to pull data." + "\n Attendance Data: " + str(
                    row) + "  \n Error Message : " + str(e)
                _logger.error(error_message)
                return error_message

        return res

    def storeData(self, row, deviceInOutCode, employeeIdMap, operatingUnitId):
        res1, res2 = super().storeData(row, deviceInOutCode, employeeIdMap, operatingUnitId)

        if deviceInOutCode:

            try:
                hr_att_pool = self.env['hr.attendance']

                employeeId = employeeIdMap.get(str(row[0]))

                if (deviceInOutCode.get(str(row[2])) == IN_CODE or deviceInOutCode.get(str(row[2])) == RFID_IN_CODE):
                    res1, res2 = self.createData(row, employeeId, IN_CODE, hr_att_pool, operatingUnitId)

                elif deviceInOutCode.get(str(row[2])) == OUT_CODE:

                    preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                                     ('check_in', '!=', False)], limit=1, order='check_in desc')

                    # preAttData = hr_att_pool.search([('employee_id', '=', employeeId)], limit=1,
                    #                                                   order='check_in desc')

                    if preAttData and preAttData.check_out is False:
                        # chk_in = self.getDateTimeFromStr(preAttData.check_in)
                        chk_in = preAttData.check_in
                        durationInHour = (self.convertDateTime(row[1]) - chk_in).total_seconds() / 60 / 60
                        if 15 >= durationInHour >= 0:
                            preAttData.write({'check_out': self.convertDateTime(row[1]),
                                              'worked_hours': durationInHour,
                                              'write_date': datetime.datetime.now(),
                                              'has_error': False,
                                              'operating_unit_id': operatingUnitId
                                              })
                            res2 = preAttData
                        else:
                            res1, res2 = self.createData(row, employeeId, OUT_CODE, hr_att_pool, operatingUnitId)
                    else:
                        res1, res2 = self.createData(row, employeeId, OUT_CODE, hr_att_pool, operatingUnitId)
                return res1, res2
            except Exception as e:
                self.env.cr.rollback()
                error_message = "Error: Unable to pull data." + "\n Attendance Data: " + "\n storeData: " + str(
                    row) + "  \n Error Message : " + str(e)
                _logger.error(error_message)
                return error_message, res2
        return res1, res2
