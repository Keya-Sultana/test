from datetime import timedelta, datetime
import time

import pytz
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class HrShifting(models.Model):
    _inherit = ['resource.calendar.attendance']

    # Fields of Model
    ot_hour_from = fields.Float(string='OT from')
    ot_hour_to = fields.Float(string='OT to')
    isIncludedOt = fields.Boolean(string='Is it included OT', default=False)
    grace_time = fields.Float(string='Grace Time', default='1.5')
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=False)

    @api.onchange('hour_from', 'hour_to')
    def _onchange_hours(self):
        # avoid negative or after midnight
        self.hour_from = min(self.hour_from, 23.99)
        self.hour_from = max(self.hour_from, 0.0)
        self.hour_to = min(self.hour_to, 24)
        self.hour_to = max(self.hour_to, 0.0)

        # avoid wrong order
        # self.hour_to = max(self.hour_to, self.hour_from)


class HrResourceCal(models.Model):
    _name = "resource.calendar"
    _description = "Hr Resource Cal"
    _inherit = ['resource.calendar', 'mail.thread']

    name = fields.Char(required=True, states={'applied': [('readonly', True)], 'approved': [('readonly', True)]})
    manager = fields.Many2one('res.users', string='Workgroup Manager', default=lambda self: self.env.uid,
                              states={'applied': [('readonly', True)], 'approved': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company',
                                 states={'applied': [('readonly', True)], 'approved': [('readonly', True)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', string='Working Time', copy=True,
                                     states={'applied': [('readonly', True)], 'approved': [('readonly', True)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')

    def _check_overlap(self, attendance_ids):
        """ attendance_ids correspond to attendance of a week,
            will check for each day of week that there are no superimpose. """
        result = []
        for attendance in attendance_ids.filtered(lambda att: not att.date_from and not att.date_to):
            # 0.000001 is added to each start hour to avoid to detect two contiguous intervals as superimposing.
            # Indeed Intervals function will join 2 intervals with the start and stop hour corresponding.
            result.append((int(attendance.dayofweek) * 24 + attendance.hour_from + 0.000001,
                           int(attendance.dayofweek) * 24 + attendance.hour_to, attendance))

        # if len(Intervals(result)) != len(result):
        #     raise ValidationError(_("Attendances can't overlap."))

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'applied'

    def action_done(self):
        self.state = 'approved'

    def action_reset(self):
        if self.state == 'approved':
            if SUPERUSER_ID == self.env.user.id:
                self.write({'state': 'draft'})
            else:
                raise UserError(_('Only Admin can reset in this stage.'))
        else:
            self.write({'state': 'draft'})

    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('You can not delete this.'))
            bill.leave_ids.unlink()
        return super(HrResourceCal, self).unlink()


class HrEmployeeShifting(models.Model):
    _inherit = ['hr.employee']

    current_shift_id = fields.Many2one('resource.calendar', compute='_compute_current_shift',
                                       string='Working Hours',
                                       check_company=True, ondelete="set null", store=True, tracking=True)
    shift_ids = fields.One2many('hr.shifting.history', 'employee_id', string='Employee Shift History')
    hours_per_day = fields.Float(related="current_shift_id.hours_per_day", )

    @api.depends('shift_ids')
    def _compute_current_shift(self):
        query = """SELECT h.shift_id FROM hr_shifting_history h
                                  WHERE h.employee_id = %s
                               ORDER BY h.effective_from DESC
                                  LIMIT 1"""
        for emp in self:
            if str(emp.id).startswith("N"):
                return None
            self._cr.execute(query, tuple([emp.id]))
            res = self._cr.fetchall()
            if res:
                emp.current_shift_id = res[0][0]
            else:
                return None

    def _get_employee_manager(self):
        manager = []
        for emp in self:
            if emp.holidays_approvers:
                for holidays_approver in emp.holidays_approvers:
                    manager.append(holidays_approver.approver)
            return manager
