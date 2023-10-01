from odoo import api, fields, models, tools, _


class InheritedHrAttendancePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on
    employee_id
    """

    _inherit = "hr.payslip"

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        return []

    def prepare_work_day_line(self, code, contract_id, number_of_days, number_of_hours, name, work_entry_type_id):
        vals = {
            'code': code,
            'contract_id': contract_id,
            'number_of_days': number_of_days,
            'number_of_hours': number_of_hours,
            'name': name,
            'work_entry_type_id': work_entry_type_id
        }
        return vals


    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if self.employee_id:
            # self.worked_days_line_ids = 0
            super(InheritedHrAttendancePayslip, self).onchange_employee()
            """
            Insert attendance data
            """
            periods = self.env['date.range'].search(
                [('date_start', '<=', self.date_from), ('date_end', '>=', self.date_to),
                 ('type_id.holiday_month', '=', 1)], limit=1)

            if not periods.id:
                return

            summary_data = self.env['hr.attendance.summary'].search([('period', '=', periods.id),
                                                                     ('state', '=', 'approved'),
                                                                     ('operating_unit_id', '=',
                                                                      self.employee_id.default_operating_unit_id.id)], limit=1)

            if not summary_data.id:
                return

            summary_line_data = self.env['hr.attendance.summary.line'].search([('att_summary_id', '=', summary_data.id),
                                                                               ('employee_id', '=',
                                                                                self.employee_id.id)], limit=1)

            if not summary_line_data.id:
                return

            work_entry_types = self.env['hr.work.entry.type'].search([])

            worked_days_lines = self.worked_days_line_ids

            if summary_line_data.leave_days:
                code = 'LEAVE100'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      summary_line_data.leave_days, 0,
                                                                                      'Leave Days',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            if summary_line_data.cal_ot_hrs:
                code = 'OT100'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      0, summary_line_data.cal_ot_hrs,
                                                                                      'OT Hours',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            ### Late Days
            if summary_line_data.late_days and len(summary_line_data.late_days) >= 0:
                code = 'LATEDAYS'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      len(summary_line_data.late_days) or 0, 0,
                                                                                      'Late Day(s)',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            ### Late Deduction Days
            if summary_line_data.deduction_days >= 0:
                code = 'LDD100'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      summary_line_data.deduction_days, 0,
                                                                                      'Late Deduction Day(s)',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            ### ABS Deduction Days
            if summary_line_data.absent_deduction_days >= 0:
                code = 'ABS100'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      summary_line_data.absent_deduction_days,
                                                                                      0,
                                                                                      'ABS Deduction Day(s)',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            ### UNPAID Holidays
            if summary_line_data.unpaid_holidays >= 0:
                code = 'LEAVE90'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      summary_line_data.unpaid_holidays,
                                                                                      0,
                                                                                      'Unpaid Holiday(s)',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            ### Not in Service Days
            if summary_line_data.nis_days > 0:
                code = 'NIS100'
                worked_days_lines += worked_days_lines.new(self.prepare_work_day_line(code, self.contract_id.id,
                                                                                      summary_line_data.nis_days,
                                                                                      0,
                                                                                      'Not-in-Service Day(s)',
                                                                                      work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code).id if work_entry_types.filtered(
                                                                                          lambda
                                                                                              t: t.code == code) else False
                                                                                      ))

            self.worked_days_line_ids = worked_days_lines
