{
    'name': 'HR Payroll Top Sheet',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'payroll',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'description': " This module shows monthly employee's salary top sheet report",
    'depends': [
        'gbs_hr_payroll',
        # 'web.report_layout',
        # 'web',
        # 'gbs_hr_attendance_report',
        # 'amount_to_word_bd',
        # 'hr_payroll',
    ],
    'data': [
        'wizard/top_sheet_wizard_view.xml',
        'report/payroll_top_sheet_report_view.xml',
    ],
    'installable': True,
    'application': True,
}
