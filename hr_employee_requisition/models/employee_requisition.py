from odoo import api, models, fields, _


class EmployeeRequisition(models.Model):
    _name = 'hr.employee.requisition'
    _description = 'Hr Employee Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Employee Requisition Ref")
    department_id = fields.Many2one('hr.department', string='Department', tracking=True, store=True)
    job_id = fields.Many2one('hr.job', string='Required Position', tracking=True, store=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
        ('valid', "Validate"),
        ('cancel', "Cancel"),
    ], string="State", default='draft', tracking=True, )

    ##### New fields
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)
    job_location = fields.Char(string='Job Location', tracking=True)
    required_position = fields.Char(string='Required Position', tracking=True)
    vacancies_no = fields.Integer(string='Number of Vacancies', tracking=True)
    position_vacant_for = fields.Selection([
        ('new', "New"),
        ('replace', "Replacement"),
        ('other', "Other"),
    ], string="Position Vacant for", tracking=True)
    gender = fields.Selection([
        ('male', "Male"),
        ('female', "Female"),
        ('other', "Other"),
    ], string="Preferred Gender", tracking=True)
    replace_name_id = fields.Many2one('hr.employee', string='Replacement of name', tracking=True)
    replace_no = fields.Char(related='replace_name_id.identification_id', string='Replacement of ID', tracking=True)
    expect_joining_date = fields.Date(string='Expected Joining Date', tracking=True)
    requisition_sub_date = fields.Date(string='Requisition Submission Date', tracking=True)
    job_description = fields.Text(string='Job Description', tracking=True)
    requisition_justification = fields.Text(string='Requisition Justification', tracking=True)
    current_employee = fields.Char(string='Existing Employee', compute='_compute_no_of_employee')
    budgeted = fields.Boolean(string='Budgeted', tracking=True)
    main_function = fields.Char(string='Main Function', tracking=True)
    additional_skills = fields.Char(string='Additional Skills ', tracking=True)

    ###### Job Specification
    year_of_experience = fields.Char(string='Years of Experience', tracking=True)
    preferred_industry = fields.Char(string='Preferred Industry', tracking=True)
    essential_education = fields.Char(string='Essential Education', tracking=True)
    preferred_education = fields.Char(string='Preferred Education', tracking=True)
    salary_range = fields.Float(string='Salary Range', tracking=True)
    language_proficency = fields.Char(string='Language Proficiency ', tracking=True)

    @api.depends('job_id')
    def _compute_no_of_employee(self):
        if self.job_id:
            pool_emp = self.env['hr.employee'].search([('job_id', '=', self.job_id.id)])
            self.current_employee = len(pool_emp.ids)
        else:
            self.current_employee = 0

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.requisition')
        return super(EmployeeRequisition, self).create(vals)

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirm'

    def action_valid(self):
        self.state = 'valid'

    def action_cancel(self):
        self.write({'state': 'cancel', 'pending_approver': None})
        self._send_refuse_notification()

    # def _compute_can_reset(self):
    #     """ User can reset a leave request if it is its own leave request or if he is an Hr Manager."""
    #     user = self.env.user
    #     # group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_user')
    #     for manpower in self:
    #         if manpower.employee_id and manpower.employee_id.user_id == user:
    #             manpower.can_reset = True

    # @api.onchange('employee_id')
    # def _onchange_employee(self):
    #     self.department_id = self.employee_id.department_id
    #     self.job_id = self.employee_id.job_id

    # def _send_refuse_notification(self):
    #     for requisition in self:
    #         if requisition.with_user(SUPERUSER_ID).employee_id and \
    #                 requisition.with_user(SUPERUSER_ID).employee_id.user_id:
    #             self.message_post(body="Your Employee Requisition request has been refused.",
    #                               partner_ids=[requisition.with_user(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    # @api.onchange('user_id')
    # def _onchange_user(self):
    #    self.work_email = self.user_id.email
    #    self.name = self.user_id.employee_ids.department_id.name
