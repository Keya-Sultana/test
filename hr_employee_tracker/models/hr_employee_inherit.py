from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _group_hr_expense_user_domain(self):
        # We return the domain only if the group exists for the following reason:
        # When a group is created (at module installation), the `res.users` form view is
        # automatically modifiedto add application accesses. When modifiying the view, it
        # reads the related field `expense_manager_id` of `res.users` and retrieve its domain.
        # This is a problem because the `group_hr_expense_user` record has already been created but
        # not its associated `ir.model.data` which makes `self.env.ref(...)` fail.
        group = self.env.ref('hr_expense.group_hr_expense_team_approver', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    department_id = fields.Many2one('hr.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    job_title = fields.Char("Job Title", compute="_compute_job_title", store=True, readonly=False, tracking=True)
    identification_id = fields.Char(string="Identification No", copy=False, tracking=True)
    mobile_phone = fields.Char('Work Mobile', tracking=True)
    work_email = fields.Char('Work Email', tracking=True)
    parent_id = fields.Many2one('hr.employee', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=True)
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', compute="_compute_work_location_id",
                                       store=True, readonly=False, tracking=True,
                                       domain="[('address_id', '=', address_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    leave_manager_id = fields.Many2one(
        'res.users', string='Time Off',
        compute='_compute_leave_manager', store=True, readonly=False, tracking=True,
        help='Select the user responsible for approving "Time Off" of this employee.\n'
             'If empty, the approval is done by an Administrator or Approver (determined in settings/users).')
    expense_manager_id = fields.Many2one(
        'res.users', string='Expense',
        domain=_group_hr_expense_user_domain,
        compute='_compute_expense_manager', store=True, readonly=False, tracking=True,
        help='Select the user responsible for approving "Expenses" of this employee.\n'
             'If empty, the approval is done by an Administrator or Approver (determined in settings/users).')

    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
    ], string='Employee Type', default='employee', required=True, tracking=True,
        help="The employee type. Although the primary purpose may seem to categorize employees, this field has also an impact in the Contract History. Only Employee type is supposed to be under contract and will have a Contract History.")

    device_id = fields.Char(string='Biometric Device ID', tracking=True)
    pin = fields.Char(string="PIN", groups="hr.group_hr_user", copy=False, tracking=True,
                      help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")

    @api.depends('parent_id')
    def _compute_expense_manager(self):
        for employee in self:
            previous_manager = employee._origin.parent_id.user_id
            manager = employee.parent_id.user_id
            if manager and manager.has_group('hr_expense.group_hr_expense_user') and (
                    employee.expense_manager_id == previous_manager or not employee.expense_manager_id):
                employee.expense_manager_id = manager
            elif not employee.expense_manager_id:
                employee.expense_manager_id = False

    last_employment_date = fields.Date(string='Last Date of Employment', tracking=True, help='Date of last employment.')
    tin_req = fields.Boolean(string='TIN Applicable', tracking=True)
    tin = fields.Char(string='TIN', tracking=True)

    # No Need Now below code
    # employee_sequence = fields.Integer("Employee Sequence", tracking=True)
    # total_pf = fields.Float(compute='_compute_total_pf', string='Total PF')

    #### Need to implement _compute_months_service considering the last employement date
    # def _compute_months_service(self):
    
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = record.name
    #         if record.job_id:
    #             name = "%s [%s]" % (name, record.job_id.name_get()[0][1])
    #         result.append((record.id, name))
    #     return result
    #
    # def _compute_total_pf(self):
    #     for name in self:
    #         payslip_line = name.sudo().env['hr.payslip.line'].search([('employee_id', '=', name.id)])
    #         for rec in payslip_line:
    #                 if rec.code == 'EPMF':
    #                     self.total_pf += abs(rec.total)



