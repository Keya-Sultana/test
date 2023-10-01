{
    'name': 'HR Employee Loan',
    'category': 'HR Employee Loan',
    'summary': 'Calculates Employees Loan',
    'description':
    """This module calculates the loan of the employee 
        based on the condition'""",
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': ['hr',
                'web',
                # 'report_layout'
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/ir_rule.xml',
        'wizards/hr_reschedule_loan.xml',
        'wizards/warning_wizard.xml',
        'views/hr_employee_loan_policy_view.xml',
        'views/hr_employee_loan_proof_view.xml',
        'views/hr_employee_loan_view.xml',
        'views/hr_employee_loan_type_view.xml',
        'views/menuitems.xml',
        'reports/hr_employee_loan_report.xml',
    ],
    'installable': True,
    'application': False,
}