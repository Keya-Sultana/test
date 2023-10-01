import time
import pytz
from odoo import models, fields, api, _, SUPERUSER_ID
from datetime import date, datetime, timedelta


class InheritHROTRequisition(models.Model):
    _inherit = 'hr.ot.requisition'

    @api.onchange('from_datetime', 'to_datetime', 'employee_id')
    def _onchange_employee_attendance(self):
        res = super(InheritHROTRequisition, self)._onchange_employee_attendance()

        for shift in self.employee_id.shift_ids:
            self.generate_ot(shift.shift_id, shift.effective_from, shift.effective_end)
        return res

    def generate_ot(self, working_schedule, start_date, end_date):
        # Attendance loop between start date and end date of employee ot requisition
        for att in self.employee_attendance_ids:
            # Employee Check Out date time
            check_out = att.check_out
            check_out = check_out + timedelta(hours=6)
            print(check_out)
            # Employee duty date
            duty_date = check_out.date()
            print(duty_date)

            for i in range(int((end_date - start_date).days) + 1):
                dt = start_date + timedelta(i)
                if dt == duty_date:
                    for wk_schedule_line in working_schedule.attendance_ids:
                        if wk_schedule_line.dayofweek == str(dt.weekday()):

                            hour_to = (wk_schedule_line.hour_to * 3600)
                            to_time_format = time.strftime("%H:%M:%S", time.gmtime(hour_to))

                            slot_end_dttime = str(dt) + " " + to_time_format

                            work_end = datetime.strptime(slot_end_dttime, '%Y-%m-%d %H:%M:%S')
                            print(work_end)

                            if check_out > work_end:
                                overtime = (check_out - work_end).total_seconds() / 3600

                                att.ot_hours = overtime


