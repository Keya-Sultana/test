from odoo import api, models, fields, _
from odoo import exceptions
from datetime import timedelta

class EmployeeAttendanceReport(models.AbstractModel):
    _name = "report.gbs_hr_attendance_report.gbs_employee_attendance_doc"
    _description = 'Employee Attendance Report'

    @api.model
    def _get_report_values(self, docids, data):

        process_date_from = "'" + str(data['date_from']) + " 00:00:00" + "'"
        process_date_to = "'" + str(data['date_to']) + " 23:59:59" + "'"

        cio_list = self.filter_data(data['employee_id'], process_date_from, process_date_to)

        try:
            cio_data, avg_working_hour = self.proces_check_in_out_data(cio_list)
        except IndexError:
            raise exceptions.Warning(
                       _('There is no attendance data for this employee')
                     )

        return {
            'data': data,
            'cio_data': cio_data,
            'avg_working_hour': avg_working_hour,
        }
        # return self.env['report'].render('gbs_hr_attendance_report.gbs_employee_attendance_doc', docargs)

    def proces_check_in_out_data(self, cio_list):
        cio_data = {}
        total_worked_minutes = 0  # Total worked minutes
        seq = 1

        for data in cio_list:
            duty_hours = self.float_to_hh_mm(data[3])
            cio_data[seq] = {}
            rec = cio_data[seq]
            rec['check_in'] = str(data[0]) if data[0] else ''
            rec['check_out'] = str(data[1]) if data[1] else ''
            rec['duty_date'] = str(data[2]) if data[2] else ''
            rec['worked_hours'] = str(duty_hours) if data[3] else ''

            # Calculate total worked minutes
            total_worked_minutes += data[3] * 60 if data[3] else 0
            seq += 1

        # Calculate average working hours and convert float to hh:mm
        average_worked_hours = str(self.float_to_hh_mm(total_worked_minutes / len(cio_list) / 60 if len(cio_list) > 0 else 0))

        return cio_data, average_worked_hours

    def filter_data(self, emo_id, from_date, to_date):

        self._cr.execute('''
        SELECT check_in + INTERVAL '6h',
               check_out + INTERVAL '6h',
               duty_date,
               worked_hours
        FROM hr_attendance
        WHERE employee_id = %s
              AND ((check_in BETWEEN %s AND %s)
              OR (check_out BETWEEN %s AND %s))
        ORDER BY check_in
        ''' % (emo_id, from_date, to_date, from_date, to_date))
        result = self._cr.fetchall()

        return result

    def float_to_hh_mm(self, hours):
        total_minutes = int(hours * 60)
        hours_part = total_minutes // 60
        minutes_part = total_minutes % 60
        return f"{hours_part:02d}:{minutes_part:02d}"
