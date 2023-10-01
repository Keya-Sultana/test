{
    "name": "Multi Level Approval",
    "version": "15.0.1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Human Resources/Approvals",
    'summary': 'Create and validate approvals requests',
    'website': 'www.odoo.com.bd',
    'images': ['static/description/icon.png'],
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/multi_level_approval_category_views.xml',
        'views/mla_category_approver_views.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}



