# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.payment.tests.common import PaymentCommon


class SSLCOMMERZCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.sslcommerz = cls._prepare_acquirer('sslcommerz', update_values={
            'sslcommerz_email_account': 'dummy@test.mail.com',
            'fees_active': False,
        })

        # Override default values
        cls.acquirer = cls.sslcommerz
        cls.currency = cls.currency_euro
