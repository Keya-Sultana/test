from odoo import api
from odoo import models, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime


class HROTRequisition(models.Model):
    _name = 'hr.ot.requisition'
    _description = "HR OT Requisition"
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

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

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  default=_default_employee, required=True, tracking=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    from_datetime = fields.Datetime('Start Date', readonly=True, index=True, copy=False, required=True, tracking=True)
    to_datetime = fields.Datetime('End Date', readonly=True, copy=False, required=True, tracking=True)
    total_hours = fields.Float(string='Total hours', compute='_compute_total_hours', store=True, digits=(15, 2),
                               readonly=True, tracking=True)
    ot_reason = fields.Text(string='Reason for OT')
    user_id = fields.Many2one('res.users', string='User', related_sudo=True, store=True,
                              default=lambda self: self.env.uid, readonly=True)
    employee_attendance_ids = fields.Many2many('hr.attendance', string='Employee Attendance')

    # approver field
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.employee.ot.approbation', 'ot_ids', string='Approvals', readonly=True)
    ##

    state = fields.Selection([
        ('to_submit', "To Submit"),
        ('to_approve', "To Approve"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='to_submit', tracking=True)

    ####################################################
    # Business methods
    ####################################################
    @api.onchange('from_datetime', 'to_datetime', 'employee_id')
    def _onchange_employee_attendance(self):
        if self.employee_id and self.from_datetime and self.to_datetime:
            from_date = self.from_datetime.date()
            from_date = str(from_date) + ' 00:00:00'
            from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')

            to_date = self.to_datetime.date()
            to_date = str(to_date) + ' 23:59:59'
            to_date = datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S')
            hr_attendance = self.env['hr.attendance'].search(
                [('check_in', '>=', from_date),
                 ('check_in', '<=', to_date),
                 ('employee_id', '=', self.employee_id.id)])
            self.update({
                'employee_attendance_ids': [(6, 0, hr_attendance.ids)]
            })

    @api.model
    def _notify_employee(self):
        for ot in self:
            if ot.sudo(SUPERUSER_ID).employee_id and \
                    ot.sudo(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your OT request has been Approved.",
                                  partner_ids=[ot.sudo(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    def _compute_current_user_is_approver(self):
        if self.pending_approver.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    @api.model
    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    @api.constrains('from_datetime', 'to_datetime')
    def _check_to_datetime_validation(self):

        for ot in self:
            if ot.to_datetime < ot.from_datetime:
                raise ValidationError(_("End Time can not less then Start Time!!"))
        domain = [
            ('from_datetime', '<=', ot.to_datetime),
            ('to_datetime', '>=', ot.from_datetime),
            ('employee_id', '=', ot.employee_id.id),
            ('id', '!=', ot.id),
            ('state', 'not in', ['refuse']),
        ]
        domainOT = self.search_count(domain)
        if domainOT:
            raise ValidationError(_('You can not have multiple OT requisition on same day!'))

    @api.depends('from_datetime', 'to_datetime')
    def _compute_total_hours(self):
        if self.from_datetime and self.to_datetime:
            start_dt = fields.Datetime.from_string(self.from_datetime)
            finish_dt = fields.Datetime.from_string(self.to_datetime)
            diff = finish_dt - start_dt
            hours = float(diff.total_seconds() / 3600)
            self.total_hours = hours

    @api.constrains('total_hours')
    def _check_values(self):
        if self.total_hours == 0.0:
            raise ValidationError(_('Duration time should not be zero!!'))

    def action_submit(self):
        self.write({'state': 'to_approve'})

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
            if is_last_approbation:
                ot.action_validate()
            else:
                vals = {'state': 'to_approve'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                ot.write(vals)
                self.env['hr.employee.ot.approbation'].create(
                    {'ot_ids': ot.id, 'approver': self.env.uid, 'sequence': sequence, 'date': fields.Datetime.now()})

    def action_validate(self):
        for ot in self:
            ot.write({'state': 'approved'})
            ot._notify_employee()

    def action_refuse(self):
        self.write({'state': 'refuse'})

    def action_reset(self):
        self.write({'state': 'to_submit'})

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
        res._notify_approvers()
        return res

    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[
                0].approver.id
        res = super(HROTRequisition, self).write(values)
        return res

    def unlink(self):
        for a in self:
            if a.state != 'to_submit':
                raise UserError(_('You can not delete this.'))
            return super(HROTRequisition, self).unlink()

    # Showing batch
    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['to_approve'])]

    ### mail notification
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
