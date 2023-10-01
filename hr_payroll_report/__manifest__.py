# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll Report",

    'summary': """
        Shows payslip reports""",

    'description': """
        This module shows HR Manager to print individual payslip PDF report.
    """,

    'author': "Odoo Bangladesh",
    'website': "",

    'category': 'payroll',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll_community',],

    # always loaded
    'data': [
         # 'wizard/salary_report_wizard.xml',
         'views/inherit_hr_department_view.xml',
         'reports/paperformat.xml',
         'reports/payroll_report_view.xml',
    ],
}