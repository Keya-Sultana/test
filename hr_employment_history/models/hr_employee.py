from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employment_history_ids = fields.One2many('hr.employment.history',
                                   'employee_id',
                                   'Employment History',
                                   help="Employment History")

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments')