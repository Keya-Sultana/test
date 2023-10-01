# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..sslcommerz_response_status import REFUND_STATUS, REFUND_INIT_STATUS


class RefundReasonWizard(models.TransientModel):
    _name = "refund.reason.wizard"

    name = fields.Text('Refund Reason', required=True)
    payment_tran_id = fields.Many2one('payment.transaction', string='Payment Transaction', default=lambda self: self.env.context.get('view_id'))

    def refund(self):
        tran_id = self.payment_tran_id
        if not (tran_id and tran_id.acquirer_reference and tran_id.acquirer_id.provider == 'sslcommerz'):
            return {'type': 'ir.actions.act_window_close'}
        sslcomz = tran_id.acquirer_id._sslcommerz_object()
        response = sslcomz.init_refund(tran_id.acquirer_reference, tran_id.amount, self.name)
        if response.get('status') == 'failed' and not response.get('refund_ref_id'):
            raise ValidationError(_(f"{REFUND_INIT_STATUS[response['status']]} - {response.get('errorReason')}"))
        tran_id.refund_ref_id = response['refund_ref_id']
        refund_status = sslcomz.query_refund_status(response['refund_ref_id'])
        tran_id.refund_message = f"{REFUND_STATUS[refund_status['status']]}"
        if refund_status.get('initiated_on') and refund_status.get('initiated_on') != '0000-00-00 00:00:00':
            tran_id.date_refund_init = refund_status['initiated_on']
        if refund_status.get('refunded_on') and refund_status.get('refunded_on') != '0000-00-00 00:00:00':
            tran_id.date_refund = refund_status['refunded_on']
        return {'type': 'ir.actions.act_window_close'}
