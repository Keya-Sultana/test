import logging
import math
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class MaternityTemplate(models.Model):
    _name = 'hr.maternity.template'
    _description = "Maternity Template"
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, tracking=True, copy=False, default='draft')
    pay_days = fields.Integer("Pay Days", required=True)
    last_payslip_count = fields.Integer("Last Payslip Count", required=True)
    line_ids = fields.One2many('hr.maternity.template.line', 'template_id', string='Salary Rules')

    # sal_rule_ids = fields.Many2many('hr.salary.rule', 'hr_maternity_salary_rules', 'template_id', 'rule_id',
    #                                 string='Salary Rules')

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirm'

    def action_validate(self):
        self.state = 'validate'

    def action_cancel(self):
        self.state = 'cancel'

    def action_refuse(self):
        self.state = 'refuse'


class MaternityTemplateLine(models.Model):
    _name = 'hr.maternity.template.line'
    _description = "Maternity Template Line"

    template_id = fields.Many2one('hr.maternity.template', string="Template", required=True)
    rule_id = fields.Many2one('hr.salary.rule', string="Salary Rule", required=True)
    mapping_code = fields.Char("Mapping Code", required=True)
    revised_pay_days = fields.Boolean('Revised Pay Days')


class MaternityHoliday(models.Model):
    _name = 'hr.maternity.holiday'
    _description = "Maternity Leave"
    _rec_name = 'employee_id'
    _order = "date_from desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

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
                                  states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                  required=True, default=_default_employee)
    template_id = fields.Many2one('hr.maternity.template', string="Template", index=True, copy=True, required=True,
                                  domain=[('state', '=', 'validate')])
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', default='draft',
        help="The status is set to 'To Submit', when a request is created." +
             "\nThe status is 'To Approve', when request is confirmed by user." +
             "\nThe status is 'Refused', when request is refused by manager." +
             "\nThe status is 'Approved', when request is approved by manager.")
        # readonly=True, track_visibility='onchange', copy=False, default='draft',
        # help="The status is set to 'To Submit', when a request is created." +
        #      "\nThe status is 'To Approve', when request is confirmed by user." +
        #      "\nThe status is 'Refused', when request is refused by manager." +
        #      "\nThe status is 'Approved', when request is approved by manager.")
    report_note = fields.Text('HR Comments')

    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True,
                              compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False, required=True,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_to = fields.Date('End Date', readonly=True, copy=False,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    notes = fields.Text('Reasons', readonly=True,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days_temp = fields.Integer('Allocation', readonly=True, copy=False,
                                         states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Integer('Number of Days', compute='_compute_number_of_days', store=True)
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', string='Department',
                                    readonly=True, store=True)
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
    maternity_allowance = fields.Float("Total Allowance", readonly=True, copy=False)
    ex_salary_amount = fields.Float("Existing Salary", readonly=True, copy=False)
    ex_salary_days = fields.Integer("Salary Days", readonly=True, copy=False)
    last_calculation_time = fields.Datetime("Calculation Time", readonly=True, copy=False)

    joining_after_leave = fields.Date("Joining Date After Leaves", readonly=True, index=True, copy=False, required=True,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})

    # Approval process
    pending_approver = fields.Many2one('hr.employee', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    approbations = fields.One2many('hr.maternity.holiday.approbation', 'maternity_id', string='Approvals', readonly=True)
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending transfered approver user',
                                                       compute="_compute_pending_transfered_approver_user",
                                                       search='_search_pending_transfered_approver_user')

    def action_calculate(self):

        payslip_pool = self.env['hr.payslip']
        for leave in self:
            amount = 0
            total_days_in_payslip = 0
            payslip_count = leave.template_id.last_payslip_count

            # applicable_rules = []
            # for l in leave.template_id.line_ids:
            #     applicable_rules.append(l.rule_id.id)

            payslips = payslip_pool.search([
                                            ('type', '=', '0'),
                                            ('state', '=', 'done'),
                                            ('employee_id', '=', leave.employee_id.id)], limit=payslip_count)

            for payslip in payslips:
                total_days_in_payslip += payslip.days_in_period
                for line in payslip.line_ids:
                    for tl in leave.template_id.line_ids:
                        if line.salary_rule_id.id == tl.rule_id.id:
                            amount += line.total
                            if tl.revised_pay_days:
                                for wd in payslip.worked_days_line_ids:
                                    if tl.mapping_code == wd.code:
                                        total_days_in_payslip -= wd.number_of_days

            leave.ex_salary_amount = amount
            leave.ex_salary_days = total_days_in_payslip
            leave.maternity_allowance = round((amount / total_days_in_payslip) * leave.template_id.pay_days)
            leave.last_calculation_time = fields.Datetime.now()

    @api.depends('number_of_days_temp')
    def _compute_number_of_days(self):
        for holiday in self:
            holiday.number_of_days = holiday.number_of_days_temp

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.department_id = self.employee_id.department_id

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

        # if employee_id:
        #     employee = self.env['hr.employee'].browse(employee_id)
        #     resource = employee.resource_id.sudo()
        #     if resource and resource.calendar_id:
        #         hours = resource.calendar_id.get_working_hours(from_dt, to_dt, resource_id=resource.id,
        #                                                        compute_leaves=True)
        #         uom_hour = resource.calendar_id.uom_id
        #         uom_day = self.env.ref('product.product_uom_day')
        #         if uom_hour and uom_day:
        #             return uom_hour._compute_quantity(hours, uom_day)

        time_delta = to_dt - from_dt
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """ If there are no date set for date_to, automatically set one 8 hours later than
            the date_from. Also update the number_of_days.
        """
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            self.date_to = date_to = datetime.strftime((fields.Date.from_string(date_from) + timedelta(days=1)),
                                                       "%Y-%m-%d")
            self.date_from = date_from = datetime.strftime((fields.Date.from_string(date_from)), "%Y-%m-%d")

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
        else:
            self.number_of_days_temp = 0

    def _compute_can_reset(self):
        """ User can reset a leave request if it is its own leave request or if he is an Hr Manager."""
        user = self.env.user
        # group_hr_manager = self.env.ref('hr_holidays.group_hr_holidays_user')
        for holiday in self:
            if holiday.employee_id and holiday.employee_id.user_id == user:
                holiday.can_reset = True

    ####################################################
    # ORM Overrides methods
    ####################################################

    # def name_get(self):
    #     res = []
    #     for leave in self:
    #         res.append((leave.id, _("%s on %s : %.2f day(s)") % (
    #         leave.employee_id.name or leave.category_id.name, leave.holiday_status_id.name, leave.number_of_days_temp)))
    #     return res

    def _check_state_access_right(self, vals):
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.env[
            'res.users'].has_group('hr_holidays.group_hr_holidays_user'):
            return False
        return True

    def add_follower(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if employee.user_id:
            self.message_subscribe_users(user_ids=employee.user_id.ids)

    def unlink(self):
        for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
            raise UserError(_('You cannot delete a leave which is in %s state.') % (holiday.state,))
        return super(MaternityHoliday, self).unlink()

    ####################################################
    # Business methods
    ####################################################

    # def _create_resource_leave(self):
    #     """ This method will create entry in resource calendar leave object at the time of holidays validated """
    #     for leave in self:
    #         self.env['resource.calendar.leaves'].create({
    #             'name': leave.name,
    #             'date_from': leave.date_from,
    #             'holiday_id': leave.id,
    #             'date_to': leave.date_to,
    #             'resource_id': leave.employee_id.resource_id.id,
    #             'calendar_id': leave.employee_id.resource_id.calendar_id.id
    #         })
    #     return True

    # def _remove_resource_leave(self):
    #     """ This method will create entry in resource calendar leave object at the time of holidays cancel/removed """
    #     return self.env['resource.calendar.leaves'].search([('holiday_id', 'in', self.ids)]).unlink()

    def _send_refuse_notification(self):
        for holiday in self:
            if holiday.with_user(SUPERUSER_ID).employee_id and \
                    holiday.with_user(SUPERUSER_ID).employee_id.user_id:
                self.message_post(body="Your Maternity leave request has been refused.",
                                  partner_ids=[holiday.with_user(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_refuse(self):
        self.write({'state': 'refuse', 'pending_approver': None})
        self._send_refuse_notification()

    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'manager_id': manager.id if manager else False})
            else:
                holiday.action_validate()

    def action_confirm(self):
        for maternity in self:
            if maternity.employee_id.holidays_approvers:
                maternity.pending_approver = maternity.employee_id.holidays_approvers[0].approver.id
                self.message_post(body="You have been assigned to approve a Maternity Leave.",
                                  partner_ids=[maternity.pending_approver.with_user(SUPERUSER_ID).user_id.partner_id.id])

            if self.filtered(lambda holiday: holiday.state != 'draft'):
                raise UserError(_('Leave request must be in Draft state ("To Submit") in order to confirm it.'))
            maternity.state = 'confirm'


    def btn_action_approve(self):
        for maternity in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None
            for approver in maternity.employee_id.holidays_approvers:
                sequence = sequence + 1
                if maternity.pending_approver.id == approver.approver.id:
                    if sequence == len(maternity.employee_id.holidays_approvers):
                        is_last_approbation = True
                    else:
                        next_approver = maternity.employee_id.with_user(SUPERUSER_ID).holidays_approvers[sequence].approver

            self.env['hr.maternity.holiday.approbation'].create(
                {'maternity_id': maternity.id, 'approver_id': self.env.uid, 'sequence': sequence,
                 'date': fields.Datetime.now()})

            if is_last_approbation:
                maternity._notify_employee()
                maternity.action_validate()
            else:
                vals = {'state': 'confirm'}
                if next_approver and next_approver.id:
                    vals['pending_approver'] = next_approver.id
                    if next_approver.with_user(SUPERUSER_ID).user_id:
                        self.sudo().message_post(body="You have been assigned to approve a Maternity Leave.",
                                                             partner_ids=[next_approver.with_user(
                                                                 SUPERUSER_ID).user_id.partner_id.id])
                maternity.sudo().write(vals)

        #self._notify_approvers()

    def action_validate(self):
        if not self.env.user.has_group('hr.group_hr_manager'):
            raise UserError('Only an HR Manager can Validate Employee Maternity Leave.')
        for requisition in self:
            requisition.pending_approver = False
            self.write({'state': 'validate'})

    def _notify_employee(self):
        for holiday in self:
                if holiday.with_user(SUPERUSER_ID).employee_id and \
                        holiday.with_user(SUPERUSER_ID).employee_id.user_id:
                    self.message_post(body="Your leave request has been Approve.",
                                      partner_ids=[holiday.with_user(SUPERUSER_ID).employee_id.user_id.partner_id.id])

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

    # def _prepare_create_by_category(self, employee):
    #     self.ensure_one()
    #     values = {
    #         'name': self.name,
    #         'type': self.type,
    #         'holiday_type': 'employee',
    #         'holiday_status_id': self.holiday_status_id.id,
    #         'date_from': self.date_from,
    #         'date_to': self.date_to,
    #         'notes': self.notes,
    #         'number_of_days_temp': self.number_of_days_temp,
    #         'parent_id': self.id,
    #         'employee_id': employee.id
    #     }
    #     return values

    # def action_validate(self):
    #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
    #         raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))
    #
    #     manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #     for holiday in self:
    #         if holiday.state not in ['confirm', 'validate1']:
    #             raise UserError(_('Leave request must be confirmed in order to approve it.'))
    #         if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
    #             raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))
    #
    #         holiday.write({'state': 'validate'})
    #         if holiday.double_validation:
    #             holiday.write({'manager_id2': manager.id})
    #         else:
    #             holiday.write({'manager_id': manager.id})
    #         if holiday.holiday_type == 'employee' and holiday.type == 'remove':
    #             meeting_values = {
    #                 'name': holiday.display_name,
    #                 'categ_ids': [
    #                     (6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
    #                 'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
    #                 'description': holiday.notes,
    #                 'user_id': holiday.user_id.id,
    #                 'start': holiday.date_from,
    #                 'stop': holiday.date_to,
    #                 'allday': False,
    #                 'state': 'open',  # to block that meeting date in the calendar
    #                 'privacy': 'confidential'
    #             }
    #             # Add the partner_id (if exist) as an attendee
    #             if holiday.user_id and holiday.user_id.partner_id:
    #                 meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]
    #
    #             meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
    #             holiday._create_resource_leave()
    #             holiday.write({'meeting_id': meeting.id})
    #         elif holiday.holiday_type == 'category':
    #             leaves = self.env['hr.holidays']
    #             for employee in holiday.category_id.employee_ids:
    #                 values = holiday._prepare_create_by_category(employee)
    #                 leaves += self.with_context(mail_notify_force_send=False).create(values)
    #             # TODO is it necessary to interleave the calls?
    #             leaves.action_approve()
    #             if leaves and leaves[0].double_validation:
    #                 leaves.action_validate()
    #     return True

    # def action_refuse(self):
    #     if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
    #         raise UserError(_('Only an HR Officer or Manager can refuse leave requests.'))
    #
    #     manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #     for holiday in self:
    #         if holiday.state not in ['confirm', 'validate', 'validate1']:
    #             raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))
    #
    #         if holiday.state == 'validate1':
    #             holiday.write({'state': 'refuse', 'manager_id': manager.id})
    #         else:
    #             holiday.write({'state': 'refuse', 'manager_id2': manager.id})
    #         # Delete the meeting
    #         if holiday.meeting_id:
    #             holiday.meeting_id.unlink()
    #         # If a category that created several holidays, cancel all related
    #         holiday.linked_request_ids.action_refuse()
    #     self._remove_resource_leave()
    #     return True

    ####################################################
    # Messaging methods
    ####################################################

    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'validate':
            return 'hr_maternity_holiday.mt_maternity_approved'
        elif 'state' in init_values and self.state == 'validate1':
            return 'hr_maternity_holiday.mt_maternity_first_validated'
        elif 'state' in init_values and self.state == 'confirm':
            return 'hr_maternity_holiday.mt_maternity_confirmed'
        elif 'state' in init_values and self.state == 'refuse':
            return 'hr_maternity_holiday.mt_maternity_refused'
        return super(MaternityHoliday, self)._track_subtype(init_values)

    def _notification_recipients(self, message, groups):
        """ Handle HR users and officers recipients that can validate or refuse holidays
        directly from email. """
        groups = super(MaternityHoliday, self)._notification_recipients(message, groups)

        self.ensure_one()
        hr_actions = []
        if self.state == 'confirm':
            app_action = self._notification_link_helper('controller', controller='/hr_holidays/validate')
            hr_actions += [{'url': app_action, 'title': _('Approve')}]
        if self.state in ['confirm', 'validate', 'validate1']:
            ref_action = self._notification_link_helper('controller', controller='/hr_holidays/refuse')
            hr_actions += [{'url': ref_action, 'title': _('Refuse')}]

        new_group = (
            'group_hr_holidays_user', lambda partner: bool(partner.user_ids) and any(
                user.has_group('hr_holidays.group_hr_holidays_user') for user in partner.user_ids), {
                'actions': hr_actions,
            })

        return [new_group] + groups

    def amount_to_text(self, amount_total):
        amt_to_word = self.env['res.currency'].amount_to_word(amount_total)
        return amt_to_word
