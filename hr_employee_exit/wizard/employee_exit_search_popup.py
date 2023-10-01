from odoo import api, fields, models, _


class EmployeeExitSearch(models.TransientModel):
    _name = 'hr.exit.employee.exit.search.popup'
    _description = 'Employee Exit Search'

    employee_id = fields.Many2one('hr.employee', string='Name of Employee', required=True,
                                  help='Please select employee name.')

    # @api.multi
    def action_search_employee_exit(self):
        return True
