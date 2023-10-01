# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug
from odoo import http
from odoo.http import request
from sslcommerz_lib import SSLCOMMERZ
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing

_logger = logging.getLogger(__name__)

# https://www.odoo.com/forum/help-1/odoo-13-user-session-is-logging-out-on-redirect-back-from-payment-gateway-175865


class SSLCommerzController(http.Controller):
    _return_url = '/payment/sslcommerz/return'
    _notify_url = "/payment/sslcommerz/ipn"
    _fail_url = "/payment/sslcommerz/fail"
    _cancel_url = "/payment/sslcommerz/cancel"

    @http.route('/payment/sslcommerz/return', type='http', auth="public", csrf=False)
    def sslcommerz_return(self, **post):
        """ SSLCOMMERZ return """
        _logger.info('Beginning SSLCOMMERZ form_feedback with post data %s', pprint.pformat(post))
        self._sslcommerz_validate_data(**post)
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/sslcommerz/fail', '/payment/sslcommerz/cancel'], type='http', auth='public', csrf=False)
    def sslcommerz_unsuccessful(self, **post):
        request.env['payment.transaction'].sudo().form_feedback(post, 'sslcommerz')
        return werkzeug.utils.redirect('/payment/process')

    def _sslcommerz_validate_data(self, **post):
        resp = post.get('status')
        if resp:
            if resp in ['VALID', 'VALIDATED']:
                _logger.info('SSLCOMMERZ: validated data')
            elif resp == 'INVALID_TRANSACTION':
                _logger.warning('SSLCOMMERZ: payment refunded to user and closed the transaction')
            else:
                _logger.warning('SSLCOMMERZ: unrecognized sslcommerz answer, received %s instead of VALID/VALIDATED and INVALID_TRANSACTION' % (post['status']))
        if post.get('tran_id'):
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', post['tran_id'])])
            post['reference'] = tx.reference
            PaymentPostProcessing.add_payment_transaction(tx)
            return request.env['payment.transaction'].sudo().form_feedback(post, 'sslcommerz')
        return False

    def _sslcommerz_validate_notification(self, **post):
        sslcommerz = request.env['payment.acquirer'].sudo().search([('provider', '=', 'sslcommerz')])
        sslcz = SSLCOMMERZ({'store_id': sslcommerz.sslcommerz_store_id, 'store_pass': sslcommerz.sslcommerz_store_pass, 'issandbox': sslcommerz.state != 'test'})
        if sslcz.hash_validate_ipn(post):
            response = sslcz.validationTransactionOrder(post['val_id'])
        else:
            return ""
        _logger.info('Validate sslcommerz Notification %s' % pprint.pformat(post))
        if response.get('status') == 'VALID':
            self._sslcommerz_validate_data(**post)
            return 'success'
        return ""

    @http.route('/payment/sslcommerz/ipn', type='http', auth='public', methods=['POST'], csrf=False)
    def sslcommerz_notify(self, **post):
        """ SSLCOMMERZ Notify """
        _logger.info('Beginning SSLCOMMERZ notification form_feedback with post data %s', pprint.pformat(post))
        return self._sslcommerz_validate_notification(**post)

