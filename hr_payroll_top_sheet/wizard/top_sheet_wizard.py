from odoo import models, fields, api


class PayslipReportWizard(models.TransientModel):
    _inherit = "payslip.report.wizard"

    def process_top_sheet_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        # return self.env['report'].get_action(self,'gbs_hr_payroll_top_sheet.report_top_sheet',data)
        return self.env.ref('hr_payroll_top_sheet.action_report_top_sheets').report_action(None, data=data)
