{
    'name': 'HR Employee Other Allowance',
    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",
    'category': 'HR Other Allowance',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': ['hr',
                'hr_work_entry_contract',
                'hr_payroll',
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/hr_other_allowance_by_employees_views.xml',
        'views/hr_other_allowance_type.xml',
        'views/hr_other_allowance.xml',
    ],

    'summary': 'Calculates HR Other Allowance Information',
    'description':
        """This module calculates the  other allowance of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}