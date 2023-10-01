from datetime import datetime
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__.split('.')[-1])

class Company(models.Model):
    _inherit = 'res.company'

    lead_notification_channel_id = fields.Many2one(
        'slack.channel', string="Lead Notification Channel", domain="[('company_id', '=', id)]")


class LeadNotification(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        # _logger.info('STEP 1')
        # _logger.info('OVERRIDE CREATE STARTED')

        res = super(LeadNotification, self).create(vals)

        if self.env.user.email == 'api@binaryquest.com':
            self.lead_notification(lead=vals)

        # _logger.info('OVERRIDE CREATE RETURNED res OBJECT')

        return res

    def _prepare_lead_notification_message(self, lead):
        # _logger.info('STEP 3')
        # _logger.info('PREPARING MESSAGE FROM LEAD')

        today = datetime.today()

        msg = f'>Lead [_{today.strftime("%A, %B %d, %Y")}_]\n'

        msg += '```'

        if lead.get("contact_name"):
            msg += f'Contact Name: {lead["contact_name"]}'

        if lead.get("phone"):
            msg += f'\nPhone: {lead["phone"]}'

        if lead.get("email_from"):
            msg += f'\nEmail: {lead["email_from"]}'

        if lead.get("description") and lead["description"] != '<p><br></p>':
            msg += f'\nDescription: {lead["description"]}'

        if lead.get("partner_name"):
            msg += f'\nOrganization Name: {lead["partner_name"]}'

        msg += '```\n\n'

        # _logger.info(f"MESSAGE PREPARED: \n {msg}")

        return msg

    def send_lead_notification_msg_for_slack(self, msg):
        # _logger.info("STEP 4")
        # _logger.info(f"MESSAGE RECEIVED: \n {msg}")
        # _logger.info(f"SLACK CHANNEL ID: {self.env.user.company_id.lead_notification_channel_id}")

        if not self.env.user.company_id.lead_notification_channel_id:
            _logger.warning("LEAD NOTIFICATION CHANNEL ID NOT FOUND OR INACCESSIBLE")
            
            return
            
        if msg:
            # _logger.info('SENDING MESSAGE TO SLACK')

            self.env.user.company_id.lead_notification_channel_id.post_message_webhook(
                msg)

    def lead_notification(self, lead):
        # _logger.info(f"STEP 2")
        # _logger.info(f"LEAD RECEIVED: \n {lead}")

        msg = self._prepare_lead_notification_message(lead=lead)

        # _logger.info('CALLING SEND NOTIFICATION')

        self.send_lead_notification_msg_for_slack(msg=msg)
