import pytz
import logging
import datetime
from odoo import fields, models, api
from .stellar_api import StellarAPI

_logger = logging.getLogger(__name__)


class StellarMachine(models.Model):
    _inherit = 'biometric.base.device'

    type = fields.Selection(selection_add=[("stellar", "Stellar")])
    auth_user = fields.Char(string='Username', required=True, tracking=True)
    password = fields.Char(string='Password', required=True, tracking=True)
    auth_code = fields.Char(string='auth_code', required=True, tracking=True)

    def create_datetime(self, date, time, gmt):
        atten_time = date + " " + time
        atten_time = datetime.datetime.strptime(atten_time, '%Y-%m-%d %H:%M:%S')
        if not gmt:
            local_tz = pytz.timezone(self.tz or self.env.user.partner_id.tz or 'GMT')
            local_dt = local_tz.localize(atten_time, is_dst=None)
            utc_dt = local_dt.astimezone(pytz.utc)
            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
            atten_time = datetime.datetime.strptime(
                utc_dt, "%Y-%m-%d %H:%M:%S")
            return atten_time
        return atten_time

    def prepare_fetch_log_params(self):
        today = fields.Datetime.now()
        if not self.last_updated_time:
            start_date = str(today).split(" ")[0].replace(str(today).split(" ")[0][-2:], "01")

            ### Need to consider timezone for start_time
            start_time = "00:00:01"
            current_datetime = start_date + " " + start_time
            dt_object = datetime.datetime.strptime(current_datetime, "%Y-%m-%d %H:%M:%S")
            if today > dt_object + datetime.timedelta(days=6):
                end_datetime = dt_object + datetime.timedelta(days=7)
                end_date, end_time = str(end_datetime).split(" ")[0], str(end_datetime).split(" ")[1]
                self.last_updated_time = self.create_datetime(end_date, end_time, False)
            else:
                end_date, end_time = str(today).split(" ")[0], str(today).split(" ")[1]
                self.last_updated_time = self.create_datetime(end_date, end_time, False)
        else:
            start_date = str(self.last_updated_time).split(" ")[0]
            start_time = str(self.last_updated_time).split(" ")[1][:8]
            if today > self.last_updated_time + datetime.timedelta(days=6):
                end_date, end_time = str(self.last_updated_time + datetime.timedelta(days=6)).split(" ")[0], \
                    str(self.last_updated_time + datetime.timedelta(days=6)).split(" ")[1]
                self.last_updated_time = self.create_datetime(end_date, end_time, True)
            else:
                end_date = str(today).split(" ")[0]
                end_time = str(today).split(" ")[1][:8]
                self.last_updated_time = self.create_datetime(end_date, end_time, True)

        return {
            'auth_user': self.auth_user,
            'auth_code': self.auth_code,
            'start_date': start_date,
            'end_date': end_date,
            'start_time': start_time,
            'end_time': end_time
        }

    def process_raw_attendance(self, device_id, employee_device_id, punched_time):
        employee_obj = self.env['hr.employee'].search([('identification_id', '=', employee_device_id)])
        _logger.info("Process Raw Attendance / Log: %s ", employee_obj)

        if not employee_obj:
            return False

        new_punched_time = punched_time.astimezone(pytz.timezone(employee_obj.resource_calendar_id.tz)).strftime('%Y-%m-%d %H:%M:%S')
        access_date = new_punched_time.split(" ")[0]
        identify_checkin_or_checkout = self.identify_checkin_or_checkout(employee_obj, punched_time)

        att_obj = self.env['hr.attendance']
        if identify_checkin_or_checkout == 1:
            att_obj.create({'employee_id': employee_obj.id,
                            'check_in': punched_time})
            # access time is checkin

        elif identify_checkin_or_checkout == 0:
            return self.insert_check_out_data(employee_obj, access_date, punched_time)
            # access time is checkout
        else:
            # this data has issue
            return False

        return True

    def insert_check_out_data(self, employee_obj, access_date, atten_time):
        intial_time = self.create_datetime(access_date, "00:00:01", False)
        data = self.env['hr.attendance'].search([('employee_id', '=', employee_obj.id),
                                                 ('check_in', '>=', intial_time),
                                                 ('check_in', '<=', atten_time),
                                                 ('check_out', '=', False)])
        if data:
            data.write({'check_out': atten_time})
            return True
        return False

    def check_close_data(self, employee_device_id, punched_datetime):
        if self.env['biometric.device.attendance'].search(
                [('employee_device_id', '=', employee_device_id),
                 ('punching_time', '>=', punched_datetime - datetime.timedelta(seconds=15)),
                 ('punching_time', '<=', punched_datetime + datetime.timedelta(seconds=15))]):
            return True
        return False

    def manual_fetch_event(self):
        super().manual_fetch_event()
        for device in self:
            if device.type == 'stellar':
                params = device.prepare_fetch_log_params()
                log = StellarAPI.fetch_log(params['auth_user'], params['auth_code'], params['start_date'],
                                           params['end_date'])
                if log:
                    for vals in log:
                        ### skip close data

                        ### Check Duplicate Pucning / Access Time

                        ### insert into machine attendace
                        vals['device_id'] = self.id
                        converted_datetime = self.create_datetime(vals['access_date'], vals['access_time'], False)
                        if not self.check_close_data(vals['registration_id'], converted_datetime):
                            new_vals = {'device_id': self.id, 'unit_name': vals['unit_name'],
                                        'employee_device_id': vals['registration_id'], 'department': vals['department'],
                                        'access_time': vals['access_time'], 'access_date': vals['access_date'],
                                        'user_name': vals['user_name'], 'unit_id': vals['unit_id'],
                                        'card': vals['card'], 'punching_time': converted_datetime}
                            res = self.env['biometric.device.attendance'].create(new_vals)
                            _logger.info("Insert Machine Attendance / Log")

                            if device.process_raw_attendance(self.id, vals['registration_id'], converted_datetime):
                                res.write({'process_status': True})
