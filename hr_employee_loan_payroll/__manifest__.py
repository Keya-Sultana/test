# -*- coding: utf-8 -*-
{
    'name': "Loan Integration With Payroll",
    'description': """
        This module integrate employees monthly mobile bill with payroll.
    """,
    'summary': """
        This module integrate employees monthly mobile bill with payroll.""",
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'version': "1.0.0",
    'license': 'LGPL-3',
    "depends": [
        # 'hr',
        # 'l10n_in_hr_payroll',
        'hr_payroll',
        'hr_employee_loan'
    ],
    'data': [
        'data/hr_payroll_data.xml',
    ],
    'installable': True,
    'application': False,
}
