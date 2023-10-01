{
    'name': 'HR Employee Other Deduction',
    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",
    'category': 'HR Other Deduction',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'depends': ['hr',
                'hr_work_entry_contract',
                'hr_payroll',
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'wizard/hr_other_deduction_by_employees_views.xml',
        'views/hr_other_deduction_type.xml',
        'views/hr_other_deduction.xml',
    ],

    'summary': 'Calculates HR Other Deduction Information',
    'description':
        """This module calculates the  other deduction of the employee
            based on the condition'""",
    'installable': True,
    'application': True,
}