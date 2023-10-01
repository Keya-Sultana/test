# -*- coding: utf-8 -*-
{
    'name': "Attendance Integration With Payroll",
    'description': """
        This module integrate employees monthly mobile bill with payroll.
    """,
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'version': "1.0.0",
    'license': 'LGPL-3',
    "depends": [
        'hr',
        'hr_payroll',
        'l10n_in_hr_payroll',
        # 'hr_employee_loan',
        'hr_attendance_and_ot_summary',
    ],
    'data': [
        'views/hr_contract_view.xml',
    ],
    'summary': """
        This module integrate employees monthly mobile bill with payroll.""",
    'installable': True,
    'application': True,
}
