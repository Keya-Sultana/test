{
    'name': 'Employee Seniority',
    'summary': 'Keep Track of Length of Employment',
    'version': "1.0.0",
    'category': 'Human Resources',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_contract',
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'views/employee_views.xml',
    ],
    'installable': True,
}
