from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class InheritHRPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    ref = fields.Char('Reference')


class InheritHRPayslip(models.Model):
    _inherit = "hr.payslip"

    ref = fields.Char('Reference')

    @api.onchange('employee_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if self.employee_id:
            self.input_line_ids = False
            super(InheritHRPayslip, self)._onchange_employee()

            """
            Incorporate other payroll data
            """
            other_line_ids = self.input_line_ids
            other_datas = self.env['hr.other.allowance.line'].search([('employee_id', '=', self.employee_id.id),
                                                                      ('state', '=', 'approved'),
                                                                      (
                                                                      'parent_id.allowance_date', '>=', self.date_from),
                                                                      ('parent_id.allowance_date', '<=', self.date_to)])
            other_type = self.env.ref('hr_other_allowance_payroll.allowance_other_input', raise_if_not_found=False)

            """
            Other Allowance Bills
            """
            allowance_amount = False
            for other_data in other_datas:
                allowance_amount += other_data.other_allowance_amount

            if self.contract_id.id:
                other_line_ids += other_line_ids.new({
                    'name': 'Other Allowance',
                    'code': "OAS",
                    'amount': allowance_amount or 0,
                    'contract_id': self.contract_id.id,
                    'input_type_id': other_type.id,
                    # 'ref': str(other_data.id),
                })

                self.input_line_ids = other_line_ids

    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        ## Below code write for state change of Other Allowance Line
        other_datas = self.env['hr.other.allowance.line'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('state', '=', 'approved'),
                                                                  ('parent_id.allowance_date', '>=', self.date_from),
                                                                  ('parent_id.allowance_date', '<=', self.date_to)])
        for line_state in other_datas:
            if self.contract_id.id:
                line_state.write({'state': 'adjusted'})

        return res



    # @api.multi
    # def action_payslip_done(self):
    #     res = super(InheritHRPayslip, self).action_payslip_done()
    #
    #     other_ids = []
    #     pay_slip_input = []
    #     for input in self.input_line_ids:
    #         if input.code == 'OAS' and input.ref:
    #             other_ids.append(int(input.ref))
    #             pay_slip_input.append(input.id)
    #
    #     other_line_pool = self.env['hr.other.allowance.line']
    #     other_data = other_line_pool.browse(other_ids)
    #     if other_data.exists():
    #         other_data.write({'state': 'adjusted'})
    #     elif len(other_ids) > 0:
    #         raise ValidationError(_("Other allowance Data Error For: " + self.name + " hr_payslip_id :" + str(
    #             self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(
    #             pay_slip_input) + ", existing ref : " + str(other_ids)))
    #
    #     return res

