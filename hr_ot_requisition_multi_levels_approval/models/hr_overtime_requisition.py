from odoo import api
from odoo import models, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class HROTRequisition(models.Model):
    _inherit = 'hr.ot.requisition'

    @api.model
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

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.ot.approbation', 'ot_ids', string='Approvals', readonly=True)

    ####################################################
    # Business methods
    ####################################################

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id and self.employee_id.holidays_approvers:
            self.pending_approver = self.employee_id.holidays_approvers[0].approver.id
        else:
            self.pending_approver = False

    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    def action_approve(self):
        for ot in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in ot.employee_id.holidays_approvers:
                sequence = sequence + 1
                if ot.pending_approver.id == approver.approver.id:
                    if sequence == len(ot.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = ot.employee_id.holidays_approvers[sequence].approver

            self.env['hr.employee.ot.approbation'].create(
                {'ot_ids': ot.id, 'approver': self.env.uid, 'sequence': sequence, 'date': fields.Datetime.now()})

            if is_last_approbation:
                ot._notify_employee()
                ot.action_validate()
            else:
                vals = {'state': 'to_approve'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                #     if next_approver.sudo(SUPERUSER_ID).user_id:
                #         self.suspend_security().message_post(body="You have been assigned to approve a loan.",
                #                                              partner_ids=[next_approver.sudo(
                #                                                  SUPERUSER_ID).user_id.partner_id.id])
                # ot.suspend_security().write(vals)
                ot.write(vals)

    def action_validate(self):
        for ot in self:
            ot.write({'state': 'approved'})
            ot.pending_approver = False
            ot._notify_employee()

    ####################################################
    # Override methods
    ####################################################

    @api.model
    def create(self, vals):
        if vals.get('employee_id', False):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            if employee and employee.holidays_approvers and employee.holidays_approvers[0]:
                vals['pending_approver'] = employee.holidays_approvers[0].approver.id
        res = super(HROTRequisition, self).create(vals)
        # res._notify_approvers()
        return res

    @api.model
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[
                0].approver.id
        res = super(HROTRequisition, self).write(values)
        return res

    # mail notification
    def _notify_approvers(self):
        approvers = self.employee_id._get_employee_manager()
        if not approvers:
            return True
        for approver in approvers:
            self.sudo(SUPERUSER_ID).add_follower(approver.id)
            if approver.sudo(SUPERUSER_ID).user_id:
                self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                    [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True
