{
    "name": "Multi Level for Stock Indent",
    "version": "15.0.1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Human Resources/Inventory",
    'summary': 'Create and validate Stock Indent requests',
    'website': 'www.odoo.com.bd',
    # 'images': ['static/description/icon.png'],
    'depends': ['stock_indent','multi_level_approval'],
    'data': [
        'views/stock_indent_mla_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
