# ©  2017 Md Mehedi Hasan <md.mehedi.info@gmail.com>

import datetime
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _default_leave_year_id(self):
        return self.env.context.get('leave_year_id')

    leave_year_id = fields.Many2one('date.range', string="Leave Year", default=_default_leave_year_id,
                                    domain="[('type_id.holiday_year', '=', True)]")

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for holiday in self:
            domain = [
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>=', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                # ('type', '=', holiday.type),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))
            # elif holiday.type == 'remove':
            ###### Convert date to datetime
            date_start = holiday.leave_year_id.date_start
            date_start = datetime(date_start.year, date_start.month, date_start.day)

            date_end = holiday.leave_year_id.date_end
            date_end = datetime(date_end.year, date_end.month, date_end.day)

            ##############
            if holiday.date_from >= date_start and holiday.date_to <= date_end:
                pass
            else:
                raise ValidationError(_('Leave duration starting date and ending date should be same year!!'))

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            res_date = self.date_from
        else:
            res_date = fields.Date.today().strftime('%Y-%m-%d')

        # self.env.cr.execute(
        #     "SELECT * FROM date_range  WHERE '{}' between date_start and date_end".format(res_date))
        # years = self.env.cr.dictfetchone()
        years = self.env['date.range'].search([('date_start', '<=', res_date),
                                               ('date_end', '>=', res_date),
                                               ('type_id.holiday_year', '=', True)], limit=1, order='id desc')

        if not years:
            raise ValidationError(_('Unable to apply leave request. Please contract your administrator.'))
        # year_id = years['id']
        year_id = years.id
        self.leave_year_id = year_id

    def _prepare_create_by_category(self, employee):
        values = super(HrLeave, self)._prepare_create_by_category(employee)
        values['leave_year_id'] = self.leave_year_id.id
        return values


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    def _default_leave_year_id(self):
        today = fields.Date.today().strftime('%Y-%m-%d')
        holiday_yr = self.env['date.range'].search([('date_start', '<=', today),
                                               ('date_end', '>=', today),
                                               ('type_id.holiday_year', '=', True)], limit=1, order='id desc')
        return holiday_yr.id or False

    leave_year_id = fields.Many2one('date.range', string="Leave Year", default=_default_leave_year_id, required=True,
                                    domain="[('type_id.holiday_year', '=', True)]")

