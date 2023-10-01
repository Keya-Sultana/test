{
    "name": "Multi Level Approval Employee Exit",
    "version": "15.0.1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Human Resources/Exit",
    'summary': 'Create and validate Exit requests',
    'website': 'www.odoo.com.bd',
    'images': ['static/description/icon.png'],
    'depends': ['multi_level_approval', 'hr_employee_exit'],
    'data': [
        'views/employee_exit_lines_views.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
