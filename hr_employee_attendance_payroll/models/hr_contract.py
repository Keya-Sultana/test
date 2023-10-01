
from odoo import fields, api, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    ot_wage = fields.Float(string='Overtime Wage')
    working_hour = fields.Float(string="Working Hour Per Day", digits='Payroll', tracking=True)
