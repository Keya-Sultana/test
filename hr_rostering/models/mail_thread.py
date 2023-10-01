from odoo import api, fields, models, SUPERUSER_ID


class HMailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    # ------------------------------------------------------
    # Followers API
    # ------------------------------------------------------

    def message_subscribe_users(self, user_ids=None, subtype_ids=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
        if user_ids is None:
            user_ids = [self._uid]
        return self.message_subscribe(self.env['res.users'].browse(user_ids).mapped('partner_id').ids,
                                      subtype_ids=subtype_ids)

    def _message_auto_subscribe_notify(self, partner_ids):
        """ Notify newly subscribed followers of the last posted message.
            :param partner_ids : the list of partner to add as needaction partner of the last message
                                 (This excludes the current partner)
        """
        if not partner_ids:
            return

        if self.env.context.get('mail_auto_subscribe_no_notify'):
            return

        # send the email only to the current record and not all the ids matching active_domain !
        # by default, send_mail for mass_mail use the active_domain instead of active_ids.
        if 'active_domain' in self.env.context:
            ctx = dict(self.env.context)
            ctx.pop('active_domain')
            self = self.with_context(ctx)

        for record in self:
            record.message_post_with_view(
                'mail.message_user_assigned',
                composition_mode='mass_mail',
                partner_ids=[(4, pid) for pid in partner_ids],
                auto_delete=True,
                auto_delete_message=True,
                parent_id=False, # override accidental context defaults
                subtype_id=self.env.ref('mail.mt_note').id)