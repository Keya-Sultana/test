{
    'name': 'BQuick HR Employee Transfer',
    'version': "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'summary': 'This module handles of HR employee transfer',
    'description': "",
    'depends': [
        'hr',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_transfer_view.xml',
        'views/hr_emp_transfer_view.xml',
    ],
    'installable': True,
    'application': False,
}
