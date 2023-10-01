import datetime

from odoo import api, fields, models, _


class AttendanceDashboard(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def retrieve_dashboard(self):
        # dateformat = self.env['res.lang'].search([])
        # print(dateformat)
        # time_format = self.env['res.lang'].search([]).time_format
        # date_format = self.env['res.lang'].search([]).date_format
        today = fields.datetime.now()
        # today = datetime.datetime.strptime(fields.datetime.now(), date_format + ' ' + time_format)
        print(today)
        result = {'last_data_pull': today}
        return result

    def sync_manually(self):
        hr_att_device_pool = self.env['hr.attendance.device.detail']
        hr_att_device_pool.sudo().pull_automation()
        return True
