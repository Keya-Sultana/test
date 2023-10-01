from odoo import api,models,fields
from odoo.tools.misc import formatLang


class LoanReport(models.AbstractModel):
    _name = "report.hr_employee_loan.report_hr_employee_loan"
    _description = 'Employee Loan Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        loan_obj = self.env['hr.employee.loan'].browse(docids[0])

        data = {'loan_name': loan_obj.name,
                'employee_name': loan_obj.employee_id.name,
                'department_name': loan_obj.department_id.name,
                'loan_type': loan_obj.loan_type_id.name,
                'principal_amount': formatLang(self.env, loan_obj.principal_amount),
                'interst_mode': loan_obj.interst_mode_id,
                'rate': loan_obj.req_rate,
                'applied_date': loan_obj.applied_date,
                'approved_date': loan_obj.approved_date,
                'disbursement_date': loan_obj.disbursement_date,
                'repayment_date': loan_obj.repayment_date,
                'amount_receive': formatLang(self.env, (loan_obj.principal_amount) - (loan_obj.remaining_loan_amount)),
                'amount_due': formatLang(self.env, loan_obj.remaining_loan_amount)}

        installment_list = []
        policies_list = []
        if loan_obj.line_ids:
            for line in loan_obj.line_ids:
                list_obj = {'num_installment': line.num_installment,
                            'schedule_date': line.schedule_date,
                            'installment': formatLang(self.env, line.installment),
                            'state': line.state}
                installment_list.append(list_obj)

        if loan_obj.employee_loan_policy_ids:
            for policy in loan_obj.employee_loan_policy_ids:
                policy_obj = {'name': policy.name,
                              'code': policy.code,
                              'type': policy.policy_type_id,
                              'value': policy.value}
                policies_list.append(policy_obj)

        return {
            'data': data,
            'lists': installment_list,
            'policies_list': policies_list,
            'policys': loan_obj.employee_loan_policy_ids

        }
        # return self.env['report'].render('hr_employee_loan.report_hr_employee_loan',docargs)