{
    "name": "Multi Level Approval",
    "version": "16.0.1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Human Resources/Approvals",
    'summary': 'Create and validate approval requests',
    'website': 'www.odoo.com.bd',
    'images': ['static/description/icon.png'],
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/multi_level_approval_rule_views.xml',
        'views/mla_rule_approver_views.xml',
        'views/menu.xml',
        'views/mla_res_user_inherit.xml',
        'views/res_config_settings_views.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
