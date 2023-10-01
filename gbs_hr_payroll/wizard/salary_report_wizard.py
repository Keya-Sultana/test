from odoo import models, fields, api


class PayslipReportWizard(models.TransientModel):
    _name = "payslip.report.wizard"
    _description = "Payslip Report Wizard"

    def process_cash_salary_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        data['report_type'] = 'cash'
        # return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_payslip', data)
        return self.env.ref('gbs_hr_payroll.action_report_individual_paslips').report_action(None, data=data)

    def process_payslip_summary_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        data['report_type'] = 'all'
        # return self.env['report'].get_action(self, 'gbs_hr_payroll.report_individual_payslip', data)
        return self.env.ref('gbs_hr_payroll.action_report_individual_paslips').report_action(None, data=data)

    def process_pf_report(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        # return self.env['report'].get_action(self,'gbs_hr_payroll.report_provident_fund_unit_wise',data)
        return self.env.ref('gbs_hr_payroll.action_provident_fund_unit_wise').report_action(None, data=data)

    def process_loan_deduction_print(self):
        data = {}
        data['active_id'] = self.env.context.get('active_id')
        # return self.env['report'].get_action(self,'gbs_hr_payroll.report_monthly_loan_deduction',data)
        return self.env.ref('gbs_hr_payroll.action_monthly_loan_deduction').report_action(None, data=data)

    # def process_top_sheet_print(self):
    #     data = {}
    #     data['active_id'] = self.env.context.get('active_id')
    #     # return self.env['report'].get_action(self,'gbs_hr_payroll_top_sheet.report_top_sheet',data)
    #     return self.env.ref('hr_payroll_top_sheet.action_report_top_sheets').report_action(None, data=data)
