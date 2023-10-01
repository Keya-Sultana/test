from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_sequence = fields.Integer("Employee Sequence")
