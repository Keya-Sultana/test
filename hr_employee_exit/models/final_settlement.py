from odoo import fields, api, models, _


class FinalSettlement(models.Model):
    _name = "final.settlement"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    _description = 'Employee Final Settlement'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, tracking=True)
    # employee_code = fields.Char('Employee Id', related='employee_id.identification_id', readonly=True)
    work_location = fields.Char('Work Location', related='employee_id.work_location', readonly=True)
    emp_designation = fields.Many2one('hr.job', string='Designation', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', readonly=True,
                                    tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    settlement_date = fields.Date(string='Settlement Date', tracking=True)
    permanent_date = fields.Date(string='Permanent Date', tracking=True)
    joining_date = fields.Date(related='employee_id.initial_employment_date', string='Date of Join', readonly=True,
                               tracking=True)
    leaving_date = fields.Date(string='Last Working Date', readonly=True, tracking=True)
    remark = fields.Text(string='Remark', tracking=True)
    exit_req_id = fields.Many2one('hr.emp.exit.req', ondelete="cascade")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('approved', ' Approved'),
    ], string='Status', default='draft', tracking=True)

    def action_confirm(self):
        self.state = 'validate'

    def action_reset(self):
        self.state = 'draft'

    def action_approved(self):
        self.state = 'approved'


class FinalSettlementLine(models.Model):
    _name = "final.settlement.line"
    _description = 'Final Settlement Line'


class Payments(models.Model):
    _name = "final.settlement.payments"
    _description = 'Final Settlement Payments'


class Deductions(models.Model):
    _name = "final.settlement.deduction"
    _description = 'Final Settlement Deduction'
