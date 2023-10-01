from odoo import api, fields, models, _, SUPERUSER_ID


class HrEmployee(models.Model):
    _inherit = 'hr.employment.history'

    address = fields.Char('Address')
    last_salary_drawn = fields.Integer('Last Salary Drawn')
    reasons_for_leaving = fields.Text('Reasons for Leaving')
