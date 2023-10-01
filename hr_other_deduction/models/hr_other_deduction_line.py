from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError


class HrOtherDeductionLine(models.Model):
    _name = 'hr.other.deduction.line'
    _description = 'HR Employee Other Deduction line'

    other_deduction_amount = fields.Float(string="Amount", readonly=True, tracking=True,
                                          states={'draft': [('readonly', False)]})
    other_deduction_remark = fields.Text(string="Remark", readonly=True, tracking=True,
                                         states={'draft': [('readonly', False)]})

    """ Relational Fields """
    parent_id = fields.Many2one(comodel_name='hr.other.deduction', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade', tracking=True)
    other_deduction_type = fields.Many2one('hr.other.deduction.type', string='Deduction Type', readonly=True,
                                           states={'draft': [('readonly', False)]})

    _sql_constraints = [
        ('unique_employee_id', 'unique(parent_id, employee_id, other_deduction_type)',
         'Warning!!: You can not use the same Deduction Type'),
    ]

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
        ('adjusted', "Adjusted")
    ], default='draft', tracking=True)

    # Show a msg for minus value
    @api.onchange('other_deduction_amount')
    def _onchange_bill(self):
        if self.other_deduction_amount < 0:
            raise UserError(_('Amount never take negative value!'))
