{
    'name': "BD Account Tax",
    'description': """BD Account Tax""",
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        'account',
        'date_range',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tds_date_range_type.xml',
        'views/inherit_date_range_view.xml',
        'views/inherit_account_tax_view.xml',
        # 'views/inherit_account_invoice_view.xml',
        'views/tax_menuitem.xml'
    ],
    'installable': True,
}