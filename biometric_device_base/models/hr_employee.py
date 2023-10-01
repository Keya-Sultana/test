from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ### Need to implement unique constraint
    employee_device_id = fields.Char(size=20, string="Employee Device ID", tracking=True)
