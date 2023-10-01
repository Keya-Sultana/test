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
            od_line_ids = self.input_line_ids
            od_datas = self.env['hr.other.deduction.line'].search([('employee_id', '=', self.employee_id.id),
                                                                   ('state', '=', 'approved'),
                                                                   ('parent_id.deduction_date', '>=', self.date_from),
                                                                   ('parent_id.deduction_date', '<=', self.date_to)])

            deduction_type = self.env.ref('hr_other_deduction.deduction_other_input', raise_if_not_found=False)

            deduction_amount = False
            for od_data in od_datas:
                deduction_amount += od_data.other_deduction_amount

            if self.contract_id.id:
                od_line_ids += od_line_ids.new({
                    'name': 'Other Deduction',
                    'code': "ODS",
                    'amount': deduction_amount or 0,
                    'contract_id': self.contract_id.id,
                    'input_type_id': deduction_type.id,
                    # 'ref': str(od_data.id),
                })

                self.input_line_ids = od_line_ids

    def action_payslip_done(self):
        res = super(InheritHRPayslip, self).action_payslip_done()

        ## Below code write for state change of Other Deduction Line
        other_datas = self.env['hr.other.deduction.line'].search([('employee_id', '=', self.employee_id.id),
                                                                  ('state', '=', 'approved'),
                                                                  ('parent_id.deduction_date', '>=', self.date_from),
                                                                  ('parent_id.deduction_date', '<=', self.date_to)])
        for line_state in other_datas:
            if self.contract_id.id:
                line_state.write({'state': 'adjusted'})

        return res



    # @api.multi
    # def action_payslip_done(self):
    #     res = super(InheritHRPayslip, self).action_payslip_done()
    #
    #     od_ids = []
    #     pay_slip_input = []
    #     for input in self.input_line_ids:
    #         if input.code == 'ODS' and input.ref:
    #             od_ids.append(int(input.ref))
    #             pay_slip_input.append(input.id)
    #
    #     od_line_pool = self.env['hr.other.deduction.line']
    #     od_data = od_line_pool.browse(od_ids)
    #     if od_data.exists():
    #         od_data.write({'state': 'adjusted'})
    #     elif len(od_ids) > 0:
    #         raise ValidationError(_("Other deduction Data Error For: " + self.name + " hr_payslip_id :" + str(
    #             self.id) + ". Need to Update 'ref' from hr_pay_slip_input where id is :" + str(
    #             pay_slip_input) + ", existing ref : " + str(od_ids)))
    #
    #     return res

