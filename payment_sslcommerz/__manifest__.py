# -*- coding: utf-8 -*-
{
    'name': 'SSLCOMMERZ Payment Acquirer',
    'version': '1.0.0',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'Accounting/Payment Acquirers',
    'summary': """Payment Acquirer: SSLCommerz Implementation""",
    'description': """SSLCommerz Payment Acquirer""",
    'license': 'OPL-1',
    "external_dependencies": {"python": ["sslcommerz-lib"]},
    'depends': ['payment'],
    'images': ['static/description/banner.png'],
    'data': [
        'data/payment_icon_data.xml',
        'views/sslcommerz_views.xml',
        'views/payment_sslcommerz_templates.xml',
        'data/payment_acquirer_data.xml',

        'wizard/refund_reason_wizard.xml',
        # 'views/payment_transaction_views.xml',
    ],
    'installable': True,
    # 'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
    'currency': 'USD'
}
