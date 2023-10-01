{
    'name': 'HR Employee Tracker',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'Human Resources',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'summary': 'Shows job titles and employee tin informations and Tracker ',
    'description':
        "This module shows job titles when searching employee name",
    'depends': [
        'hr',
        'hr_employee_seniority',
        # 'base_suspend_security'
    ],
    'data': [
        "views/hr_employee_view.xml",

    ],
    'installable': True,
    'application': False,
}
