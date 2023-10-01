#-*- coding:utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

class Loan(models.Model):
    _name = 'hr.employee.loan'
    _inherit = ['hr.employee.loan','mail.thread']

    @api.multi
    def _default_approver(self):
        default_approver = 0
        employee = self._default_employee()
        if isinstance(employee, int):
            emp_obj = self.env['hr.employee'].search([('id', '=', employee)], limit=1)
            if emp_obj.sudo().holidays_approvers:
                default_approver = emp_obj.sudo().holidays_approvers[0].approver.id
        else:
            if employee.sudo().holidays_approvers:
                default_approver = employee.sudo().holidays_approvers[0].approver.id
        return default_approver

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_current_employee, required=True)
    compute_field = fields.Boolean(string="check field", compute='get_user')
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True, default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user', related='pending_approver.user_id', related_sudo=True, store=True, readonly=True)
    current_user_is_approver = fields.Boolean(string= 'Current user is approver', compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.loan.approbation', 'loan_id', string='Approvals', readonly=True)
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending transfered approver user',compute="_compute_pending_transfered_approver_user", search='_search_pending_transfered_approver_user')
    state = fields.Selection(selection_add=[('validate', 'Validated'),('refuse', 'Reject')])
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')

    @api.multi
    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is an Hr Manager."""
        user = self.env.user
        # group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_user')
        for holiday in self:
            if holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True

    @api.depends('employee_id')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('hr_employee_loan.group_user_loan'):
            self.compute_field = True
        else:
            self.compute_field = False

    @api.model
    def create(self, values):
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                values['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(Loan, self).create(values)
        return res

    #@api.onchange('employee_id')
    #def _onchange_employee(self):
    #    if self.employee_id and self.employee_id.holidays_approvers:
     #       self.pending_approver = self.employee_id.holidays_approvers[0].approver.id
      #  else:
       #     self.pending_approver = False

    @api.multi
    def _send_refuse_notification(self):
        for holiday in self:
            if holiday.sudo(SUPERUSER_ID).employee_id and \
                    holiday.sudo(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your Short leave request has been refused.",
                                  partner_ids=[holiday.sudo(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    @api.multi
    def _notify_employee(self):
        for loan in self:
            if loan.sudo(SUPERUSER_ID).employee_id and \
                    loan.sudo(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your Loan request has been Approved.",
                                  partner_ids=[loan.sudo(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    @api.multi
    def action_refuse(self):
        self.write({'state': 'refuse', 'pending_approver': None})
        self._send_refuse_notification()

    @api.multi
    def action_reset(self):
        return self.write({'state': 'draft'})

    @api.multi
    def action_draft(self):
        super(Loan, self).action_draft()
        for loan in self:
            if loan.employee_id.holidays_approvers:
                loan.pending_approver = loan.employee_id.holidays_approvers[0].approver.id
                self.message_post(body="You have been assigned to approve a loan.", partner_ids=[loan.pending_approver.sudo(SUPERUSER_ID).user_id.partner_id.id])

    @api.multi
    def btn_action_approve(self):
        for loan in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in loan.employee_id.holidays_approvers:
                sequence = sequence + 1
                if loan.pending_approver.id == approver.approver.id:
                    if sequence == len(loan.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = loan.employee_id.sudo(SUPERUSER_ID).holidays_approvers[sequence].approver

            self.env['hr.employee.loan.approbation'].create(
                {'loan_id': loan.id, 'approver_id': self.env.uid, 'sequence': sequence,
                 'date': fields.Datetime.now()})

            if is_last_approbation:
                loan._notify_employee()
                loan.action_validate()
            else:
                vals = {'state': 'applied'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                    if next_approver.sudo(SUPERUSER_ID).user_id:
                        self.suspend_security().message_post(body="You have been assigned to approve a loan.",
                                          partner_ids=[next_approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
                loan.suspend_security().write(vals)

    @api.multi
    def action_validate(self):
        if not self.env.user.has_group('hr_employee_loan.group_manager_loan'):
           raise UserError('Only an Loan Manager can Validate loan requests.')

        for loan in self:
            loan.state = 'approved'
            loan.pending_approver = False
            loan._notify_employee()

    @api.one
    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id or self.pending_approver.transfer_holidays_approvals_to_user.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    @api.one
    def _compute_pending_transfered_approver_user(self):
        self.pending_transfered_approver_user = self.pending_approver.transfer_holidays_approvals_to_user


    def _search_pending_transfered_approver_user(self, operator, value):
        replaced_employees = self.env['hr.employee'].search([('transfer_holidays_approvals_to_user', operator, value)])
        employees_ids = []
        for employee in replaced_employees:
            employees_ids.append(employee.id)
        return [('pending_approver', 'in', employees_ids)]

