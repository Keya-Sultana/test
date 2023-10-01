from odoo import fields, models, api
from odoo.exceptions import ValidationError


class OtherDeductionType(models.Model):
    _name = "hr.other.deduction.type"
    _description = "Employee Other Deduction Type"
    _order = "id"

    name = fields.Char(string='Type Name', size=30)
    active = fields.Boolean('Active', default=True)
    payroll_ref_code = fields.Char(string='Payroll Ref Code')

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['hr.other.deduction.type'].search(
            [('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('This name is already existed')

