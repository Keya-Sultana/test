from datetime import datetime, timedelta
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__.split('.')[-1])


class Company(models.Model):
    _inherit = 'res.company'

    work_log_channel_id = fields.Many2one(
        'slack.channel', string="Work Log Channel", domain="[('company_id', '=', id)]")


class WorkLog(models.Model):
    _inherit = 'account.analytic.line'

    def _get_time_from_timedelta(self, delta):
        return str(timedelta(hours=delta)).rsplit(':')

    def _prepare_work_log_message(self, timesheets):
        # _logger.info('PREPARING WORK LOG MESSAGE')

        today = datetime.today()

        msg = f'>*Work Log Summery* [_{today.strftime("%A, %B %d, %Y")}_]\n'
        
        if not timesheets:
            _logger.info('NO TIMESHEET DATA FOUND FOR TODAYS DATE')
            
            msg += '```NO WORK LOG FOUND FOR TODAY```'
        else:
            current_user = {}
            current_idx = 0

            for idx, timesheet in enumerate(timesheets):
                if not current_user:
                    current_user['name'] = timesheet["employee_id"].name
                    current_user['employee_id'] = timesheet["employee_id"].id
                    current_user['projects'] = set()
                    current_user['tasks'] = 0
                    current_user['time'] = 0
                    current_idx += 1

                elif idx == len(timesheets)-1 or current_user['employee_id'] != timesheet["employee_id"].id:
                    hours, mins, secs = self._get_time_from_timedelta(current_user['time'])

                    msg += f'```{current_idx}. {current_user["name"]}'
                    msg += f'\nProjects: {", ".join(current_user["projects"])}'
                    msg += f'\nNo. of Tasks: {str(current_user["tasks"])}'
                    msg += f'\nTotal Time: {hours} hours and {mins} mins'
                    msg += '```\n\n'

                    current_user['name'] = timesheet["employee_id"].name
                    current_user['employee_id'] = timesheet["employee_id"].id
                    current_user['projects'] = set()
                    current_user['tasks'] = 0
                    current_user['time'] = 0
                    current_idx += 1

                current_user['projects'].add(timesheet["project_id"].name)
                
                if timesheet['task_id']:
                    current_user['tasks'] += 1
                
                if timesheet['unit_amount']:
                    current_user['time'] += float(timesheet['unit_amount'])

        # _logger.info(f'MESSAGE PREPARED: {msg}')

        return msg

    @api.model
    def get_timesheets_by_datetime(self, date):
        # _logger.info('FETCHING DATA FROM TIMESHEET POOL')

        timesheet_data = self.search([('date', '=', date.strftime('%Y-%m-%d'))], order='user_id desc')

        # _logger.info('FETCHING DATA FROM TIMESHEET POOL FINISHED')

        return timesheet_data

    def send_work_log_msg_for_slack(self, msg):
        # _logger.info(f'MESSAGE RECEIVED: {msg}')
        # _logger.info('MESSAGE SEND STARTED')

        if not self.env.user.company_id.work_log_channel_id:
            _logger.warning(
                "WORK LOG NOTIFICATION CHANNEL ID NOT FOUND OR INACCESSIBLE")

            return

        if msg and self.env.user.company_id.work_log_channel_id:
            # _logger.info('SENDING MESSAGE TO WEBHOOK')

            self.env.user.company_id.work_log_channel_id.post_message_webhook(
                msg)
            
            # _logger.info('SENDING MESSAGE TO WEBHOOK FINISHED')

    def run_work_log_notification(self):
        # _logger.info('WORK LOG STARTED')

        today = fields.datetime.now()
        # datetime.today().strftime("%d/%m/%Y")

        # _logger.info(f'DATE: {today}')
        # _logger.info('GETTING TIMESHEET')

        timesheets = self.get_timesheets_by_datetime(date=today)

        # _logger.info(f'TIMESHEETS: {timesheets}')

        msg = self._prepare_work_log_message(timesheets=timesheets)

        self.send_work_log_msg_for_slack(msg=msg)

        # _logger.info('WORK LOG NOTIFICATION ENDED')
