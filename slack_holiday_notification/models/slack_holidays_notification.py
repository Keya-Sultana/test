from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID


class Company(models.Model):
    _inherit = 'res.company'

    leave_monitor_channel_id = fields.Many2one('slack.channel', string="Leave Monitor Channel")


class Holidays(models.Model):
    _name = "hr.leave"
    _inherit = "hr.leave"

    @api.model
    def _get_holiday_by_date(self, holiday_date=None):
        if holiday_date is None:
            holiday_date = fields.Datetime.now()[:10]

        self.env.cr.execute(
            "SELECT id FROM hr_leave  WHERE '{}' between date_from and date_to".format(holiday_date))
        results = self.env.cr.dictfetchall()
        holiday_ids = [r['id'] for r in results]
        return holiday_ids

    @api.model
    def notify_slack_followers(self):
        holiday_ids = self._get_holiday_by_date()
        holidays = self.search([('id', 'in', holiday_ids)])
        if holidays:
            msg = ""
            msg += "*On Leave Today*\r\n"
            msg += "```"
            for record in holidays:
                msg += record.employee_id.name.ljust(25) + " >>  "
                msg += record.department_id.name if record.department_id else ""
                msg += "\r\n"

            msg += "```"
            self.env.user.company_id.leave_monitor_channel_id.post_message_webhook(msg)

    @api.model
    def _prepare_leave_monitoring_message(self, holiday, is_approve):
        msg = ""
        msg += "*Leave Approval Notification*\r\n" if is_approve else "*Leave Rejection Notification*\r\n"
        msg += "```"
        msg += "Employee    # " + holiday.employee_id.name + "\r\n"
        msg += "Department  # " + holiday.department_id.name + "\r\n"
        msg += "No of Days  # " + str(int(abs(holiday.number_of_days))) + "\r\n"
        msg += "Period      # " + holiday.date_from.strftime("%d-%b-%Y") + " to " + \
               holiday.date_to.strftime("%d-%b-%Y") + "\r\n"
        msg += "```"
        return msg

    def send_leave_notification(self, is_approve=False):
        for holiday in self:
            msg = self._prepare_leave_monitoring_message(holiday, is_approve)
            if msg and self.env.user.company_id.leave_monitor_channel_id:
                self.env.user.company_id.leave_monitor_channel_id.post_message_webhook(msg)

    def action_refuse(self):
        res = super(Holidays, self).action_refuse()
        self.send_leave_notification(False)
        return res

    def action_validate(self):
        res = super(Holidays, self).action_validate()
        self.send_leave_notification(True)
        return res