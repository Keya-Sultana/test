from odoo import api, fields, models
from odoo import models, fields, api, _
from odoo.osv import osv
from dateutil.relativedelta import relativedelta
from odoo import api
from odoo import models, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class HrEmployeeRequisition(models.Model):
    _name = 'hr.employee.requisition'
    _description = 'Hr Employee Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(string="Manpower Requisition Ref")
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True,
                              compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Manager', index=True, readonly=True, default=_default_employee)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Title', readonly=True, store=True)

    line_ids = fields.One2many('hr.employee.requisition.line', 'requisition_id', string="Employee Requisition")

    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
        ('valid', "Validate"),
        ('cancel', "Cancel"),
    ], string="State", default='draft', tracking=True,)

    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is an Hr Manager."""
        user = self.env.user
        # group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_user')
        for manpower in self:
            if manpower.employee_id and manpower.employee_id.user_id == user:
                manpower.can_reset = True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.requisition')
        return super(HrEmployeeRequisition, self).create(vals)


    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_id = self.employee_id.department_id
        self.job_id = self.employee_id.job_id

    def _send_refuse_notification(self):
        for requisition in self:
            if requisition.with_user(SUPERUSER_ID).employee_id and \
                    requisition.with_user(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your Employee Requisition request has been refused.",
                                  partner_ids=[requisition.with_user(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirm'

    def action_valid(self):
        self.state = 'valid'

    def action_cancel(self):
        self.write({'state': 'cancel', 'pending_approver': None})
        self._send_refuse_notification()

    #@api.onchange('user_id')
    #def _onchange_user(self):
    #    self.work_email = self.user_id.email
    #    self.name = self.user_id.employee_ids.department_id.name


