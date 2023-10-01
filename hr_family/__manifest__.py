{
    'name': 'Employee Family Information',
    'version': "1.0.0",
    'category': 'Generic Modules/Human Resources',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_children.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
}
