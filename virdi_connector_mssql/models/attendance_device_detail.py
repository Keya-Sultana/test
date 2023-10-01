import logging
import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

IN_CODE = 'IN'
OUT_CODE = 'OUT'
RFID_IN_CODE = 'IN_RFID'
VALID_DATA = "Valid"

get_BADGENUMBER = """SELECT DISTINCT (%s)
                     FROM %s 
                     WHERE IsRead = 0 AND id <= ?"""

get_att_data_sql = """SELECT
                          att.C_Unique, att.C_Date, att.C_Time
                      FROM %s att                      
                      WHERE att.IsRead = 0 
                      AND att.C_Unique is NOT NULL
                      AND att.C_Unique <> ''
                      ORDER BY att.C_Unique, att.C_Date, att.C_Time ASC"""


class AttendanceDeviceDetail(models.Model):
    _inherit = 'hr.attendance.device.detail'

    device_brand = fields.Selection(selection_add=[('virdi', 'Virdi')])

    def processData(self, attDevice, conn, cursor):

        def checkValidData(row, deviceInOutCode, employeeIdMap):
            # _logger.info(row)
            if row[0] is None:  # Check employee_device_id is not null
                return "Empty Acc No"
            if employeeIdMap.get(str(row[0])) is None:  # Check employee_device_id is mapped or not
                return "Unmapped Emp Acc"
            # if row[1] is None:  # Check in_out code is not null
            #     return "Empty Code"
            # if deviceInOutCode.get(str(row[1])) != IN_CODE and deviceInOutCode.get(
            #         str(row[1])) != RFID_IN_CODE and deviceInOutCode.get(
            #     str(row[1])) != OUT_CODE:  # Check in_out code is valid or not
            #     return "Unmapped Code"
            if row[1] is None:  # Check time is not null
                return "Empty Check Time"
            # if row[3] is None: # Check sensor_id is not null
            #     return "Empty Sensor ID"
            return VALID_DATA

        def isValidByDuration(currentRow, previousRow, deviceInOutCode, tolerableSecond):

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
            # Need to unblock
            # durationInSecond = (currentRow[2] - previousRow[2]).total_seconds()
            # if durationInSecond > tolerableSecond:
            #     return True
            # else:
            #     return False
            return True

        res = super().processData(attDevice, conn, cursor)

        if attDevice.device_brand == 'virdi':

            _logger.info("Calling processData(virdi)")
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

            sql_query = "SELECT count(*) FROM %s WHERE IsRead = 0" % db_table
            cursor.execute(sql_query)
            res = cursor.fetchone()

            # sql_query = "SELECT min(Id) FROM %s WHERE IsRead = 0" % db_table
            # cursor.execute(sql_query)
            # minId = cursor.fetchone()

            if res[0] is None:
                success_message = "Attendance data are already updated. There are no new attendance data yet."
                return

            deviceInOutCode = {}  # Where key is code and value is "IN" OR OUT

            tolerableSecond = self.getAttDeviceRulesRule()
            if tolerableSecond == 0:
                tolerableSecond = 300

            # for line_detail in attDevice.device_line_details:
            #     if line_detail.type_code == IN_CODE:
            #         deviceInOutCode[str(line_detail.type_value)] = IN_CODE
            #     elif line_detail.type_code == RFID_IN_CODE:
            #         deviceInOutCode[str(line_detail.type_value)] = IN_CODE
            #     elif line_detail.type_code == OUT_CODE:
            #         deviceInOutCode[str(line_detail.type_value)] = OUT_CODE

            # Map employee_id to employee_device_id
            employeeIdMap = attDevice.mapping_employee_ids(cursor, employee_code, db_table)

            sql_query = get_att_data_sql % db_table
            cursor.execute(sql_query)
            att_rows = cursor.fetchall()

            new_array = [(a, self.getDateTimeFromStr(b + c, '%Y%m%d%H%M%S')) for a, b, c in att_rows]

            # process_records = []
            reason = ""

            try:
                previousRow = {}

                for row in new_array:
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
                    reason = checkValidData(row, deviceInOutCode, employeeIdMap)
                    if reason != VALID_DATA:
                        if reason != "Unmapped Emp Acc":
                            raise ValidationError(reason)
                        else:
                            reason = None
                    else:
                        if isValidByDuration(row, previousRow, deviceInOutCode, tolerableSecond):
                            reason, att_rec = self.storeData(row, deviceInOutCode, employeeIdMap,
                                                             attDevice.operating_unit_id)
                        previousRow = row
                        # process_records.append(row[3])
                        vals = {'state': '1'}
                        if att_rec is not None:
                            vals['attendance_id'] = att_rec.id
                        machine_att.write(vals)

                # Store all attendance data to application database.
                # Now Update on SQL Server Database(External)

                sql_query = "UPDATE %s SET IsRead = 1 WHERE IsRead = 0" % db_table
                cursor.execute(sql_query)
                conn.commit()

                return reason

            except Exception as e:
                # if process_records:
                #     sql_query = "UPDATE %s SET IsRead = 1 WHERE IsRead = 0 AND id in {}" % db_table
                #     # cursor.execute("UPDATE iclock_transaction SET IsRead = 1 WHERE IsRead = 0 AND id in {}".format(
                #     #     tuple(process_records)))
                #     cursor.execute(sql_query.format(tuple(process_records)))
                #     conn.commit()
                #     self.env.cr.commit()
                error_message = "Error: Unable to pull data." + "\n Attendance Data: " + str(
                    row) + "  \n Error Message : " + str(e)
                _logger.error(error_message)

                return error_message

        return res

    def storeData(self, row, deviceInOutCode, employeeIdMap, operatingUnitId):
        res1, res2 = super().storeData(row, deviceInOutCode, employeeIdMap, operatingUnitId)

        if not deviceInOutCode:

            try:
                hr_att_pool = self.env['hr.attendance']

                employeeId = employeeIdMap.get(str(row[0]))

                preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                                 ('check_in', '>=', row[1].date())],
                                                limit=1, order='check_in desc')
                if preAttData:
                    chk_in = preAttData.check_in
                    durationInHour = (self.convertDateTime(row[1]) - chk_in).total_seconds() / 60 / 60
                    preAttData.write({'check_out': self.convertDateTime(row[1]),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'operating_unit_id': operatingUnitId
                                      })
                    res2 = preAttData
                else:
                    res1, res2 = self.createData(row, employeeId, IN_CODE, hr_att_pool, operatingUnitId)

                return res1, res2
            except Exception as e:
                self.env.cr.rollback()
                error_message = "Error: Unable to pull data." + "\n Attendance Data: " + "\n storeData: " + str(
                    row) + "  \n Error Message : " + str(e)
                _logger.error(error_message)
                return error_message, res2
        return res1, res2
