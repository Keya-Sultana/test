
{
    "name": "Account Currency Wrapper",
    "summary": "USD to BDT as rate input",
    'category': 'Accounting',
    'version': "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    "depends": [
        'base',
    ],
    "data": [
        'views/inherit_res_currency_view.xml',
        'views/inherit_res_currency_rate_view.xml'
    ],
    "application": False,
    "installable": True,
}