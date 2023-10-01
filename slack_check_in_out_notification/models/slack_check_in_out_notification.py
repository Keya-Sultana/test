from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID


class Company(models.Model):
    _inherit = 'res.company'

    check_in_out_channel_id = fields.Many2one('slack.channel', string="Attendance Check In Out Channel")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def notify_slack_followers(self):
        if self.attendance_state == 'checked_in':
            message = '*Checked In*'
        else:
            message = '*Checked Out*'
        msg = ""
        msg += message + " by *" + self.name + "*"
        return msg

    def send_check_in_out_notification(self):
        msg = self.notify_slack_followers()
        if msg and self.env.user.company_id.check_in_out_channel_id:
            self.env.user.company_id.check_in_out_channel_id.post_message_webhook(msg)

    def attendance_manual(self, next_action, entered_pin=None):
        res = super(HrEmployee, self).attendance_manual(next_action, entered_pin=None)
        self.send_check_in_out_notification()
        return res

    # def _attendance_action_change(self):
    #     res = super()._attendance_action_change()
    #     self.send_check_in_out_notification()
    #     return res

