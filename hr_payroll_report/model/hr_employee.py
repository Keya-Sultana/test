from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_sequence = fields.Integer("Employee Sequence")
    initial_employment_date = fields.Date(
        string='Initial Date of Employment',
        help='Date of first employment if it was before the start of the '
             'first contract in the system.', )
    employee_contract_id = fields.Many2one('hr.contract', compute='_compute_contract_id',
                                           string='Current Employee Contract', help='Latest contract of the employee')

    @api.depends('employee_contract_id', )
    def _compute_contract_id(self):
        """ get the lastest contract """

        for employee in self:
            contract = self.env['hr.contract']
            employee.employee_contract_id = contract.search([('employee_id', '=', employee.id)],
                                                            order='date_start desc', limit=1)
