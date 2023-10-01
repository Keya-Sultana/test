
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _


class Requisition(models.Model):
    _name = 'hr.employee.requisition'
    _inherit = ['hr.employee.requisition', 'mail.thread']

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

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True, default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user', related='pending_approver.user_id', related_sudo=True, store=True, readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver', compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.requisition.approbation', 'requisition_id', string='Approvals', readonly=True)
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending transfered approver user', compute="_compute_pending_transfered_approver_user", search='_search_pending_transfered_approver_user')
    #state = fields.Selection(selection_add=[('approve', 'Approved')], track_visibility='onchange')

    @api.model
    def create(self, values):
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                values['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(Requisition, self).create(values)
        return res

    def action_confirm(self):
        super(Requisition, self).action_confirm()
        for requisition in self:
            if requisition.employee_id.holidays_approvers:
                requisition.pending_approver = requisition.employee_id.holidays_approvers[0].approver.id
                self.message_post(body="You have been assigned to approve a Manpower Requisition.", partner_ids=[requisition.pending_approver.with_user(SUPERUSER_ID).user_id.partner_id.id])

    def _notify_employee(self):
        for requisition in self:
            if requisition.with_user(SUPERUSER_ID).employee_id and \
                    requisition.with_user(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your Manpower Requisition request has been Approved.",
                                  partner_ids=[requisition.with_user(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    def btn_action_approve(self):
        for requisition in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in requisition.employee_id.holidays_approvers:
                sequence = sequence + 1
                if requisition.pending_approver.id == approver.approver.id:
                    if sequence == len(requisition.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = requisition.employee_id.with_user(SUPERUSER_ID).holidays_approvers[sequence].approver

            self.env['hr.employee.requisition.approbation'].create(
                {'requisition_id': requisition.id, 'approver_id': self.env.uid, 'sequence': sequence,
                 'date': fields.Datetime.now()})

            if is_last_approbation:
                requisition._notify_employee()
                requisition.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                    if next_approver.with_user(SUPERUSER_ID).user_id:
                        self.sudo().message_post(body="You have been assigned to approve a Manpower Requisition.",
                                          partner_ids=[next_approver.with_user(SUPERUSER_ID).user_id.partner_id.id])
                requisition.sudo().write(vals)

    def action_validate(self):
        if not self.env.user.has_group('hr.group_hr_manager'):
           raise UserError('Only an HR Manager can Validate Manpower Requisition.')
        super(Requisition, self).action_valid()
        for requisition in self:
            requisition.pending_approver = False
            requisition.write({'state': 'valid'})
            requisition._notify_employee()

    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id or self.pending_approver.transfer_holidays_approvals_to_user.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    def _compute_pending_transfered_approver_user(self):
        self.pending_transfered_approver_user = self.pending_approver.transfer_holidays_approvals_to_user

    def _search_pending_transfered_approver_user(self, operator, value):
        replaced_employees = self.env['hr.employee'].search([('transfer_holidays_approvals_to_user', operator, value)])
        employees_ids = []
        for employee in replaced_employees:
            employees_ids.append(employee.id)
        return [('pending_approver', 'in', employees_ids)]

