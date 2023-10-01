# -*- coding: utf-8 -*-
import requests
from datetime import datetime
from odoo.http import json, logging
from odoo.exceptions import Warning
from odoo import api, fields, models, SUPERUSER_ID

# Initializing, the _logger object makes sure that the name of this file
# is carried along with the log messages.
_logger = logging.getLogger(__name__)


class SlackChannel(models.Model):
    _name = 'slack.channel'
    _description = "Slack Channel"

    name = fields.Char('Channel Name', required=True)
    webhook_url = fields.Char('Webhook URL', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    @api.model
    def post_message_webhook(self, message=None):
        # _logger.info(f"STEP 5 (FINAL)")
        # _logger.info(f"SLACK POST MESSAGE WEBHOOK RUNNING")
        # _logger.info(f"MESSAGE FOR SLACK: \n {message}")

        # Since this is just an extra module, most exceptions have to be handled
        # to enable other actions that may be in the pipeline to proceed
        error_msg = "Slack Notification won't be sent: "
        payload = {'text': message, 'icon_emoji': ':inbox_tray:'}
        try:
            if self.webhook_url:
                req = requests.post(
                    self.webhook_url, data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'}
                )

                # _logger.info(f"SLACK REQUEST URL: {req.url}")
                # _logger.info(f"SLACK RESPONSE: {req}")

                # Invalid slack URL will return 403 Error: Forbidden Client
                if req.status_code == 403:
                    _logger.warning(error_msg + "the Slack url is forbidden")
            
                # _logger.info(f"SLACK POST MESSAGE WEBHOOK FINISHED")

            else:
                _logger.warning("No Webhook URL Exist")
        except Exception as e:
            _logger.warning(e)


class Company(models.Model):
    _inherit = 'res.company'

    slack_channels = fields.One2many('slack.channel', 'company_id', string="Slack Channels")
