from odoo import models, fields, api


class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.attendance.duration.wizard'
    _description = 'Hr Bank Selection Wizard'

    period = fields.Many2one("date.range", string="Select Period", required=True)

    def process_report(self):

        data = {}

        data['period'] = self.period.date_start

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_hr_att_dur', data=data)

