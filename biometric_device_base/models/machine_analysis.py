import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class BiometricAttendance(models.Model):
    _name = 'biometric.device.attendance'

    @api.constrains('access_time', 'access_date', 'user_name')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    ### Need to Work

    device_id = fields.Many2one('biometric.base.device', string='Device')
    unit_name = fields.Char()
    employee_device_id = fields.Char(size=20, string="Employee Device ID")
    access_id = fields.Char()
    department = fields.Char()
    access_time = fields.Char()
    access_date = fields.Char()
    user_name = fields.Char()
    unit_id = fields.Char()
    card = fields.Char()
    process_status = fields.Boolean(default=False, string="Process Status")
    attempt_to_process = fields.Integer(string='Attempt to Process', required=False, default=0)
    punching_time = fields.Datetime(string='Punching Time')

    def process_attendance_logs_manually(self):
        for log in self:
            # vals = {
            #     ''
            # }

            _logger.info("Process Attendance Log: %s", log)
            if self.env['biometric.base.device'].process_raw_attendance(log.device_id.id, log.employee_device_id,
                                                                        log.punching_time):
                log.write({'process_status': True})
        return


# class BiometricAttendanceReport(models.Model):
#     _name = 'biometric.attendance.report'
#     _auto = False
#     _order = 'access_date desc'
#
#     ### Need to Work
#
#     user_name = fields.Many2one('hr.employee', string='Employee', help="Employee")
#     device_id = fields.Many2one('biometric.base.device', string='Device')
#     access_date = fields.Datetime(string='Date', help="Punching Date")
#     access_time = fields.Datetime(string='Punching Time', help="Punching Time")
#     card = fields.Char()
