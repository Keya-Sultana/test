{
    'name': 'HR Payroll Festival Bonus',
    'summary': 'This Module Generate Payroll Festival Bonus Summary',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'HR Payroll',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': [
        'hr_payroll',
        ],
    'data': [
        'data/data.xml',
        'views/inherited_hr_payslip.xml',
        #'views/inherit_hr_contract.xml',
    ],
    'installable': True,
    'application': False,
}