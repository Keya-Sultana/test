from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academicinfor_ids = fields.One2many('hr.employee.academic',
                                   'employee_id',
                                   'Academic Information',
                                   help="Academic Information")