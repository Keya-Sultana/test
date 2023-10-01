{
    "name": "Multi Level Purchase",
    "version": "15.0.1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Human Resources/Purchase",
    'summary': 'Create and validate purchase requests',
    'website': 'www.odoo.com.bd',
    'images': ['static/description/icon.png'],
    'depends': ['multi_level_approval', 'purchase'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
