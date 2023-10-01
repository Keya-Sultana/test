import datetime
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class Employee(models.Model):
    _inherit = "hr.employee"

    remaining_leaves = fields.Float(compute='_compute_remaining_leaves', string='Remaining Legal Leaves',
                                    inverse='_inverse_remaining_leaves',
                                    help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. '
                                         'Total based on all the leave types without overriding limit.')
    leaves_count = fields.Integer('Number of Leaves', compute='_compute_leaves_count')

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        year_id = self.get_year()
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                hr_leave h
                
            WHERE
                h.state='validate' AND
                
                h.employee_id in %s AND
                h.leave_year_id = %s
            GROUP BY h.employee_id,h.leave_year_id""", (tuple(self.ids), year_id,))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    def _compute_remaining_leaves(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.remaining_leaves = remaining.get(employee.id, 0.0)

    def _compute_leaves_count(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.leaves_count = remaining.get(employee.id)

    def get_year(self):
        year_id = 0
        curr_date = datetime.date.today().strftime('%Y-%m-%d')
        years = self.env['date.range'].search([('date_start', '<=', curr_date),
                                               ('date_end', '>=', curr_date),
                                               ('type_id.holiday_year', '=', True)], limit=1, order='id desc')
        if years:
            year_id = years.id
        return year_id

    def _compute_allocation_count(self):
        today = fields.Date.today().strftime('%Y-%m-%d')
        holiday_yr = self.env['date.range'].search([('date_start', '<=', today),
                                                    ('date_end', '>=', today),
                                                    ('type_id.holiday_year', '=', True)], limit=1, order='id desc')

        data = self.env['hr.leave.allocation'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.active', '=', True),
            ('state', '=', 'validate'),
            ('leave_year_id', '=', holiday_yr.id)
        ], ['number_of_days:sum', 'employee_id'], ['employee_id'])
        rg_results = dict((d['employee_id'][0], d['number_of_days']) for d in data)
        for employee in self:
            employee.allocation_count = float_round(rg_results.get(employee.id, 0.0), precision_digits=2)
            employee.allocation_display = "%g" % employee.allocation_count
