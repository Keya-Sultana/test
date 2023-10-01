import datetime
import pytz
from odoo import api, fields, models

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


class BiometricBaseDevice(models.Model):
    _name = 'biometric.base.device'

    name = fields.Char(string="Machine Name")
    type = fields.Selection([], string='Your biometric machine type')
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed "
                               "according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web "
                               "client.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    last_updated_time = fields.Datetime(string='Last Sync Time')

    def manual_fetch_event(self):
        return True

    def compare_with_schedule_time(self, schedule_time, access_time):
        if schedule_time - (30 / 60) <= access_time <= schedule_time + (30 / 60):
            return True
        return False

    def identify_checkin_or_checkout(self, employee_obj, punched_time):
        ### resource calender id function will return the right resource calendar id. Arguments will be employee_obj and punching_time
        ### employee_obj.shift_ids.search([('effective_end','>=',datetime.date.today()), ('effective_from','<=', datetime.date.today())]).shift_id.attendance_ids.read()
        roaster_data = employee_obj.shift_ids.search(
            [('effective_end', '>=', punched_time.date()), ('effective_from', '<=', punched_time.date())]).shift_id
        if roaster_data:
            new_punched_time = punched_time.astimezone(pytz.timezone(employee_obj.resource_calendar_id.tz)).strftime(
                '%Y-%m-%d %H:%M:%S')
            access_date = new_punched_time.split(" ")[0]
            access_time = new_punched_time.split(" ")[1]
            the_day = str(datetime.datetime.strptime(access_date, '%Y-%m-%d').weekday())
            access_time = float(access_time.replace(access_time[-3:], "").replace(":", "."))
            access_time = int(access_time) + ((access_time - int(access_time)) / 0.60)

            for r in roaster_data.attendance_ids.filtered(lambda l: l.dayofweek == the_day).read():
                if self.compare_with_schedule_time(r['hour_from'], access_time):
                    return 1

                if self.compare_with_schedule_time(r['hour_to'], access_time):
                    return 0

        return False

    def download_attendance(self):
        biometric_attendance_device = self.env['biometric.device.attendance']
        att_obj = self.env['hr.attendance']
        employee = self.env['hr.employee']
        date = '2023-01-05'
        data = biometric_attendance_device.search([('access_date', '=', date)]).read()
        for i in data:
            employee_obj = employee.search([('identification_id', '=', i.get('registration_id'))])
            time = i.get('access_time')
            access_time = float(time[:len(time) - 3].replace(":", ".").replace(" ", ""))
            if len(employee_obj) != 0:
                identify_checkin_or_checkout = self.identify_checkin_or_checkout(employee_obj, i['access_date'],
                                                                                 access_time)
                if identify_checkin_or_checkout == 1:
                    att_obj.create({'employee_id': employee_obj.id})
                    # access time is checkin
                    pass
                if identify_checkin_or_checkout == 0:
                    # access time is checkout
                    pass
                else:
                    # this data has issue
                    pass


def additional_minute(time, additional_time):
    additional_time = additional_time / 100
    t = time + additional_time
    vals = t - int(t)
    if vals >= 0.6:
        vals = vals - 0.6
        t = int(t) + 1 + vals
        return t
    return t


def subtract_time(time, subtract_time):
    subtract_time = subtract_time / 100
    t = time - subtract_time
    vals = t - int(t)
    if vals > 0.6:
        vals = vals - 0.4
        t = int(t) + vals
        return t
    return t
