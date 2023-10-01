from odoo import models, fields, api


class HrEmployeeTransfer(models.Model):
    _name = 'hr.employee.transfer'
    _inherit = ['mail.thread']
    _description = 'Hr Employee Transfer'

    @api.returns('self')
    def _default_employee_get(self):
        return self.env.user.employee_id

    name = fields.Char(string="Reference No", readonly=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee_get,
                                  tracking=True, store=True)
    joining_date = fields.Date(related='employee_id.initial_employment_date', string='Date Of Join', readonly=True)
    emp_department = fields.Many2one('hr.department', string='Department',
                                     store=True, readonly=True)
    emp_designation = fields.Many2one('hr.job', string='Designation', store=True, readonly=True)

    new_company_name = fields.Many2one('res.company', string='New Company', tracking=True, required=True)
    new_designation_id = fields.Many2one('hr.job', string='New Designation', tracking=True, required=True)
    new_dept_id = fields.Many2one('hr.department', string="New Department", tracking=True, required=True)
    new_job_location = fields.Many2one('operating.unit', string='Job Location', tracking=True, required=True)

    effective_date = fields.Date(string="Effective Date", tracking=True, required=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approve', 'Approved'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('hr.employee.transfer') or '/'
        vals['name'] = seq
        return super(HrEmployeeTransfer, self).create(vals)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.emp_designation = self.employee_id.job_id
            self.emp_department = self.employee_id.department_id

    def action_confirm(self):
        self.state = 'to approve'

    def action_done(self):
        self.state = 'approve'
        self.employee_id.write({
            'department_id': self.new_dept_id.id,
            'job_id': self.new_designation_id.id,
            'default_operating_unit_id': self.new_job_location.id,
            'company_id': self.new_company_name.id,
        })

    def action_reject(self):
        self.state = 'cancel'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    """ All relations fields """
    transfer_ids = fields.One2many('hr.employee.transfer', 'employee_id', "Employee Transfer Information")
