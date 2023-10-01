import time
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta


class HrShiftEmployeeBatch(models.Model):
    _name = 'hr.shift.employee.batch'
    _description = "Hr Shift Employee Batch"

    name = fields.Char(string='Batch Name', required=True, tracking=True)
    # effective_from = fields.Date(string='Effective Start Date', default=date.today(), tracking=True)
    # effective_end = fields.Date(string='Effective End Date', tracking=True)
    # shift_id = fields.Many2one("resource.calendar", string="Shift Name")
    company_id = fields.Many2one('res.company', string='Company', required='True', tracking=True,
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True', tracking=True,
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    shift_emp_ids = fields.One2many('hr.shifting.history', 'shift_batch_id', tracking=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('in_progress', "Assign Employee"),
        ('publish', 'Published'),
    ], default='draft', tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    def regenerate_employee_attendance_slot(self):
        for batch in self:
            for shift in batch.shift_emp_ids:
                batch.generate_emp_att_slot(shift.shift_id, shift.effective_from, shift.effective_end,
                                            shift.employee_id)
            batch.state = 'publish'

    def generate_emp_att_slot(self, working_schedule, start_date, end_date, resource):
        local_tz = pytz.timezone(working_schedule.tz or self.env.user.partner_id.tz or 'GMT')

        #### Call Delete Function
        slot_ids = self.env['planning.slot'].search(
            [('resource_id', '=', resource.resource_id.id), ('start_datetime', '>=', start_date),
             ('start_datetime', '<=', end_date)])
        slot_ids.unlink()

        # Call Create Function
        for i in range(int((end_date - start_date).days) + 1):
            dt = start_date + timedelta(i)
            for wk_schedule_line in working_schedule.attendance_ids:
                if wk_schedule_line.dayofweek == str(dt.weekday()):
                    hour_from = (wk_schedule_line.hour_from * 3600)
                    from_time_format = time.strftime("%H:%M:%S", time.gmtime(hour_from))

                    hour_to = (wk_schedule_line.hour_to * 3600)
                    to_time_format = time.strftime("%H:%M:%S", time.gmtime(hour_to))
                    slot_start_dttime = str(dt) + " " + from_time_format
                    slot_end_dttime = str(dt) + " " + to_time_format

                    start_time = datetime.strptime(slot_start_dttime, '%Y-%m-%d %H:%M:%S')
                    end_time = datetime.strptime(slot_end_dttime, '%Y-%m-%d %H:%M:%S')

                    if start_time > end_time:
                        end_time = end_time + timedelta(days=1)

                    start_local_dt = local_tz.localize(start_time, is_dst=None)
                    end_local_dt = local_tz.localize(end_time, is_dst=None)

                    sutc_dt = start_local_dt.astimezone(pytz.utc)
                    eutc_dt = end_local_dt.astimezone(pytz.utc)

                    start_utc_dt = sutc_dt.strftime("%Y-%m-%d %H:%M:%S")
                    end_utc_dt = eutc_dt.strftime("%Y-%m-%d %H:%M:%S")

                    vals = {'resource_id': resource.resource_id.id or False,
                            'role_id': resource.default_planning_role_id.id or False,
                            'start_datetime': start_utc_dt, 'end_datetime': end_utc_dt}

                    planning_obj = self.env['planning.slot']
                    planning_obj.create(vals)

        return True

    def unlink(self):
        for a in self:
            if a.state != 'draft':
                raise UserError(_('Sorry,You can not delete this.'))
        return super(HrShiftEmployeeBatch, self).unlink()


    ##### Previours unlink code
    # def unlink(self):
    #     for a in self:
    #         if str(a.effective_from) < str(date.today()):
    #             user = self.env.user.browse(self.env.uid)
    #             if user.has_group('base.group_system'):
    #                 pass
    #             else:
    #                 raise UserError(_('You can not delete this.'))
    #
    #         query = """ delete from hr_shifting_history where shift_batch_id=%s"""
    #         self._cr.execute(query, tuple([self.id]))
    #         return super(HrShiftEmployeeBatch, self).unlink()
