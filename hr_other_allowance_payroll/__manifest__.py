# -*- coding: utf-8 -*-
{
    'name': "Other Allowance Bill Integration With Payroll",
    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",
    'version': "1.0.0",
    'license': 'LGPL-3',
    'summary': """
        This module integrate employees monthly other allowance bill with payroll.""",
    'description': """
        This module integrate employees monthly other allowance bil with payroll.
    """,
    "depends": [
        'hr_other_allowance',
        'hr_payroll',
        # 'l10n_in_hr_payroll',
    ],
    'data': [
        'data/hr_payroll_data.xml',
    ],
    'installable': True,
    'application': True,
}
