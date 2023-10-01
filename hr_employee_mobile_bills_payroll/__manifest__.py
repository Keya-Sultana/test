# -*- coding: utf-8 -*-
{
    'name': "Mobile Bill Integration With Payroll",
    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",
    'category': 'Employee Mobile Bills',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'summary': """
        This module integrate employees monthly mobile bill with payroll.""",
    'description': """
        This module integrate employees monthly mobile bill with payroll.
    """,
    "depends": [
         'hr_employee_mobile_bills',
         'hr_payroll',
         # 'hr',
         # 'l10n_in_hr_payroll',
    ],
    'data': [
        'data/hr_payroll_data.xml',
    ],
    'installable': True,
    'application': True,
}
