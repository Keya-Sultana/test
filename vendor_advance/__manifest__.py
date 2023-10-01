{
    'name': "Vendor Advances",
    'description': """
        Module is responsible for 'Vendor Advances'.This module included with-
        1. Creation / Modification of Vendor Advances
        2. Deletion of Vendor Advances
        3. Accounting Treatment of Vendor Advances
        

        """,
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'category': 'Accounting & Finance',
    'depends': [
        # 'account_accountant',
        'l10n_bd_account_tax',
        # 'vendor_security_deposit',
    ],
    'data': [
        'data/data.xml',
        'security/vendor_security.xml',
        'security/ir.model.access.csv',
        'views/vendor_advance_view.xml',
        # 'views/account_invoice.xml',
        'views/receive_outstanding_advance.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}