from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InheritedHrMobilePayslip(models.Model):
    """
    Inherit HR Payslip models and add onchange functionality on 
    employee_id
    """
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.onchange('employee_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):

        if self.employee_id:
            self.input_line_ids = False
            super(InheritedHrMobilePayslip, self)._onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            mobile_datas = self.env['hr.mobile.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                                   ('state', '=', 'approved'),
                                                                   ('parent_id.bill_date', '>=', self.date_from),
                                                                   ('parent_id.bill_date', '<=', self.date_to)])

            mobile_type = self.env.ref('hr_employee_mobile_bills_payroll.mobile_other_input', raise_if_not_found=False)

            """
            Mobile Bills
            """
            bill_amount = False
            for mobile_data in mobile_datas:
                bill_amount += mobile_data.amount

            if self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Mobile Bill',
                    'code': "MOBILE",
                    'amount': bill_amount or 0,
                    'contract_id': self.contract_id.id,
                    'input_type_id': mobile_type.id,
                    # 'ref': str(mobile_data.id),
                })
                self.input_line_ids = other_line_ids

    def action_payslip_done(self):
        res = super(InheritedHrMobilePayslip, self).action_payslip_done()

        ## Below code write for state change of Other Allowance Line
        mobile_datas = self.env['hr.mobile.bill.line'].search([('employee_id', '=', self.employee_id.id),
                                                               ('state', '=', 'approved'),
                                                               ('parent_id.bill_date', '>=', self.date_from),
                                                               ('parent_id.bill_date', '<=', self.date_to)])
        for line_state in mobile_datas:
            if self.contract_id.id:
                line_state.write({'state': 'adjusted'})

        return res



    # @api.multi
    # def action_payslip_done(self):
    #     res = super(InheritedHrMobilePayslip, self).action_payslip_done()
    #
    #     mobile_ids = []
    #     pay_slip_input = []
    #     for input in self.input_line_ids:
    #         if input.code == 'MOBILE' and input.ref:
    #             mobile_ids.append(int(input.ref))
    #             pay_slip_input.append(input.id)
    #
    #     mobile_line_pool = self.env['hr.mobile.bill.line']
    #     mobile_data = mobile_line_pool.browse(mobile_ids)
    #     if mobile_data.exists():
    #         mobile_data.write({'state': 'adjusted'})
    #     elif len(mobile_ids) > 0:
    #         raise ValidationError(_("Mobile Bill Data Error For: " + self.name + " hr_payslip_id :" + str(
    #             self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(
    #             pay_slip_input) + ", existing ref : " + str(mobile_ids)))
    #
    #     return res

