from odoo import api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    employee_sequence = fields.Integer("Employee Sequence")
