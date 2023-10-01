from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    sequence = fields.Integer(string='Sequence', index=True,
                              help="Gives the sequence order when displaying "
                                   "a list of departments.")
