{
    'name': 'HR Holiday Allowance',
    'description': "This module enables employee Holiday Allowance",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'version': "1.0.0",
    'data': [
        'security/ir.model.access.csv',
        'wizard/holiday_allowance_wizard_view.xml',
        'views/holiday_allowance_view.xml'
    ],
    'depends': [
        'hr_payroll'
    ],
    'installable': True,
    'application': False,
}