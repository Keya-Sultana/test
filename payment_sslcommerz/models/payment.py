# -*- coding: utf-8 -*-

import logging
from werkzeug import urls
from sslcommerz_lib import SSLCOMMERZ
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from ..controllers.main import SSLCommerzController
from ..sslcommerz_response_status import SSLCOMMERZ_STATUS, REFUND_INIT_STATUS, REFUND_STATUS

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('sslcommerz', 'SSLCommerz')], ondelete={'sslcommerz': 'set default'})
    sslcommerz_store_id = fields.Char('Store ID', groups='base.group_user', required_if_provider='sslcommerz')
    sslcommerz_store_pass = fields.Char('Store Pass', groups='base.group_user', required_if_provider='sslcommerz')

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['fees'].append('sslcommerz')
        return res

    # def sslcommerz_get_form_action_url(self):
    #     self.ensure_one()
    #     environment = 'prod' if self.state == 'enabled' else 'test'
    #     if environment == 'prod':
    #         return 'https://securepay.sslcommerz.com'
    #     return 'https://sandbox.sslcommerz.com'

    def sslcommerz_compute_fees(self, amount, currency_id, country_id):
        """ Compute alipay fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        fees = 0.0
        if self.fees_active:
            country = self.env['res.country'].browse(country_id)
            if country and self.company_id.sudo().country_id.id == country.id:
                percentage = self.fees_dom_var
                fixed = self.fees_dom_fixed
            else:
                percentage = self.fees_int_var
                fixed = self.fees_int_fixed
            fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    def _sslcommerz_object(self):
        settings = {'store_id': self.sslcommerz_store_id, 'store_pass': self.sslcommerz_store_pass,
                    'issandbox': self.state == 'test'}
        return SSLCOMMERZ(settings)

    def sslcommerz_form_generate_values(self, values):
        base_url = self.get_base_url()
        sslcomz = self._sslcommerz_object()
        order_name = values.get('reference', '').split('-')
        products = []
        categories = []
        order = self.env['sale.order'].search([('name', '=', order_name[0])])
        # inv = self.env['account.move'].search([('account.move')])
        for order_line in order.order_line:
            products.append(order_line.product_id.name)
            categories.append(order_line.product_id.categ_id.name)
        values.update({
            'product': ','.join(products),
            'product_category': ','.join(categories),
        })

        if values.get('currency').name != 'BDT':
            # TODO: convert currency to BDT here
            # amount = rates.oe.convert(values.get('currency').name, 'BDT', values.get('amount', 0.0))
            # Initially conversion support is removed.
            raise UserError(_("Currency is not supported!. Please use BDT instead."))

        datas = {
            'total_amount': values.get('amount', 0.0),
            'currency': 'BDT',
            'product_name': values.get('product', ""),
            "product_category": values.get('product_category', ""),
            "product_profile": "general",
            "tran_id": values.get('reference', ''),
            'cus_name': values.get('partner_name'),
            'cus_email': values.get('partner_email') or "",
            'cus_phone': values.get('partner_phone') or "",
            'cus_add1': values.get('partner_address'),
            'cus_city': values.get('partner_city'),
            'cus_country': values.get('partner_country') and values.get('partner_country').name or '',
            'cus_state': values.get('partner_state') and (
                    values.get('partner_state').code or values.get('partner_state').name) or '',
            'cus_postcode': values.get('partner_zip'),
            'emi_option': 0,
            'shipping_method': "NO",
            'num_of_item': len(values.get('product').split(',')),
            "success_url": urls.url_join(base_url, SSLCommerzController._return_url),
            'fail_url': urls.url_join(base_url, SSLCommerzController._fail_url),
            'cancel_url': urls.url_join(base_url, SSLCommerzController._cancel_url),
            'ipn_url': urls.url_join(base_url, SSLCommerzController._notify_url),
            'multi_card_name': "",
        }
        response = sslcomz.createSession(datas)
        if response.get('status') != 'SUCCESS':
            raise ValidationError(_(response.get('failedreason')))

        currency = self.env['res.currency'].search([('name', '=', 'BDT')])
        datas.update({
            "currency": currency,
            "return_url": urls.url_join(base_url, SSLCommerzController._return_url),
            'notify_url': urls.url_join(base_url, SSLCommerzController._notify_url),
        })
        datas.update(response)
        self.env.context = dict(self.env.context)
        self.env.context.update({'tx_url': response.get('GatewayPageURL')})
        return datas


class TxSSLCommerz(models.Model):
    _inherit = 'payment.transaction'

    refund_message = fields.Text('Refund Message')
    refund_ref_id = fields.Char('Refund Ref.')
    date_refund_init = fields.Datetime('Refund Initiated on')
    date_refund = fields.Datetime('Refunded On')

    @api.model
    def _sslcommerz_form_get_tx_from_data(self, data):
        tran_id, amount, bank_tran_id = data.get('tran_id'), data.get('amount'), data.get('bank_tran_id')
        if not tran_id:
            _logger.info('SSLCommerz: received data with missing reference (%s)' % tran_id)
            raise ValidationError(_('SSLCommerz: received data with missing reference (%s)') % tran_id)
        if not bank_tran_id:
            _logger.info('SSLCommerz: received data with missing transaction at the bank\'s end')
            raise ValidationError(_('SSLCommerz: received data with missing transaction at the bank\'s end'))

        txs = self.env['payment.transaction'].search([('reference', '=', tran_id)])
        if not txs or len(txs) > 1:
            error_msg = _('SSLCommerz: received data for reference %s') % tran_id
            logger_msg = 'SSLCommerz: received data for reference %s' % tran_id
            if not txs:
                error_msg += _('; no order found')
                logger_msg += '; no order found'
            else:
                error_msg += _('; multiple order found')
                logger_msg += '; multiple order found'
            _logger.info(logger_msg)
            raise ValidationError(error_msg)

        # verify paid amount
        amount = float(amount)
        tx_amount = txs.amount
        if txs.currency_id.name != 'BDT':
            # TODO: convert to BDT
            # tx_amount = rates.oe.convert(txs.currency_id.name, 'BDT', txs.amount)
            raise UserError(_("{} is not supported. please use BDT instead.".format(txs.currency_id.name)))
        if round(amount, 2) != round(tx_amount, 2):
            _logger.info('SSLCommerz: amount mismatch. had to pay %s but paid %s' % (round((tx_amount * 85.34), 2),
                                                                                     round(amount, 2)))
            raise ValidationError(
                _('SSLCommerz: amount mismatch. had to pay %s but paid %s' % (round((tx_amount * 85.34), 2),
                                                                              round(amount, 2))))
        if not txs.acquirer_reference:
            txs.acquirer_reference = bank_tran_id
        return txs

    def _sslcommerz_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if self.reference and data.get('tran_id') != self.reference:
            invalid_parameters.append(('tran_id', data.get('tran_id'), self.reference))
        if not data.get('status'):
            invalid_parameters.append(('status', data.get('status'), 'something'))
        return invalid_parameters

    def _sslcommerz_form_validate(self, data):
        status = data.get('status')
        if status in ['VALID', 'VALIDATED']:
            self.write({'acquirer_reference': data.get('bank_tran_id')})
            self._set_transaction_done()
            return True
        elif status in ['FAILED', 'CANCELLED', 'INVALID_TRANSACTION', 'UNATTEMPTED', 'EXPIRED']:
            self.write({'state_message': SSLCOMMERZ_STATUS[status]})
            self._set_transaction_cancel()
            return False
        else:
            error = _('SSLCommerz: feedback error')
            _logger.info(error)
            self.write({'state_message': error})
            self._set_transaction_error()
            return False

    def update_refund_status(self):
        for record in self:
            if not record.refund_ref_id:
                return
            sslcomz = record.acquirer_id._sslcommerz_object()
            refund_status = sslcomz.query_refund_status(record.refund_ref_id)
            record.refund_message = f"{REFUND_STATUS[refund_status['status']]}"
            _logger.info("Status: %s" % REFUND_STATUS[refund_status['status']])
            if refund_status.get('refunded_on') and refund_status.get('refunded_on') != '0000-00-00 00:00:00':
                _logger.info("Refunded on: %s" % refund_status['refunded_on'])
                record.date_refund = refund_status['refunded_on']
                # TODO: need to update status of payment.transaction after refund successfully
                # TODO: need to update account.move (invoice) after successful refund
                # TODO: need to update sale order after successful refund
