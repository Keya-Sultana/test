{
    'name': 'Employee Payslip Excel Report',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'payroll',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        "views/hr_payroll_views.xml",
        'views/action_manager.xml',
    ],
    'summary': 'Shows payslip excel reports',
    'description':
        "This module shows payslip excel report ",
    'installable': True,
    'application': True,
}
