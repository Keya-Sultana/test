from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID


class Company(models.Model):
    _inherit = 'res.company'

    att_monitor_channel_id = fields.Many2one('slack.channel', string="Attendance Monitor Channel")


class DeviceDetail(models.Model):
    _inherit = 'hr.attendance.device.detail'

    @api.model
    def pull_automation(self):
        super(DeviceDetail, self).pull_automation()
        self.att_monitoring_msg_for_slack()

    # @api.model
    def att_monitoring_msg_for_slack(self):
        data = {}
        emp_pool = self.env['hr.employee']
        att_utility_pool = self.env['attendance.utility']
        curr_time_gmt = fields.datetime.now()
        current_time = curr_time_gmt + timedelta(hours=6)
        requested_date = data['required_date'] = curr_time_gmt.strftime("%Y-%m-%d")
        graceTime = att_utility_pool.getGraceTime(requested_date)
        for rec in self.search([]):
            msg = self._prepare_att_monitoring_message(rec.operating_unit_id, data, graceTime, emp_pool,
                                                       att_utility_pool, current_time)
            if msg and self.env.user.company_id.att_monitor_channel_id:
                self.env.user.company_id.att_monitor_channel_id.post_message_webhook(msg)

    @api.model
    def _prepare_att_monitoring_message(self, operating_unit, data, graceTime, emp_pool, att_utility_pool,
                                        current_time):
        pool = self.env['report.gbs_hr_attendance_report.report_daily_att_doc']
        att_summary = pool.getSummaryByUnit(operating_unit, data, graceTime, emp_pool, att_utility_pool, current_time)
        if not att_summary.get('late', False) and not att_summary.get('absent', False):
            return False

        msg = ""
        msg += "*Attendance Report*\r\n"

        msg += "```"
        msg += "Total Employee      : " + str(att_summary.get('total_emp', '')) + "\n"
        msg += "Roster Not Mapped   : " + str(len(att_summary.get('roster_obligation', ''))) + "\n"
        msg += "On time Present     : " + str(len(att_summary.get('on_time_present', ''))) + "\n"
        msg += "Late Employee       : " + str(len(att_summary.get('late', ''))) + "\n"
        msg += "Absent Employee     : " + str(len(att_summary.get('absent', ''))) + "\n"
        msg += "On Leave            : " + str(len(att_summary.get('leave', ''))) + "\n"
        msg += "```"

        if att_summary.get('late', False):
            msg += "\r\n*Late Employee*\r\n"
            msg += "```"
            for lemp in att_summary.get('late', False):
                msg += str(lemp.name).ljust(30) + " >>  " + lemp.check_in.strftime("%H:%M %p") + "\r\n"
            msg += "```"

        if att_summary.get('absent', False):
            msg += "\r\n*Absent Employee*\r\n"
            msg += "```"
            for abs in att_summary.get('absent', False):
                msg += str(abs.name) + "\r\n"
            msg += "```"

        return msg
