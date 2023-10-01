# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SSLCOMMERZ Payment Acquirer',
    'version': '2.0',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 365,
    'summary': 'Payment Acquirer: SSLCOMMERZ Implementation',
    'description': """SSLCOMMERZ Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_sslcommerz_templates.xml',
        'data/payment_acquirer_data.xml',
        'data/payment_sslcommerz_email_data.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
