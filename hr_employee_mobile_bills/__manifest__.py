{
    'name': 'Employee Mobile Bills',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'Employee Mobile Bills',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': ['hr',
                'hr_payroll',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mobile_bill_by_employees_views.xml',
        'views/hr_mobile_bill_view.xml',
        'views/hr_emp_mb_bill_view.xml',
        'views/hr_emp_mb_bill_limit_view.xml',
        'report/hr_mobile_report_templates.xml',
    ],
    
    'summary': 'Calculates Employees Mobile Bills',
    'description': 
    """This module calculates the moblile bills of the employee
        based on the condition'""",        
    'installable': True,
    'application': True,
}