{
    'name': 'GBS HR Attendance Report',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'attendance',
    'version': "15.0.1.0.0",
    'depends': [
        'hr',
        'hr_attendance',
        # 'gbs_operating_unit',
        # 'gbs_hr_employee',
        # 'hr_employee_operating_unit',
        # 'gbs_hr_attendance_utility',
        'hr_attendance_and_ot_summary'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/job_card_report_view.xml',
        # 'report/report_paperformat.xml',
        # 'wizard/hr_attendance_duration_wizard_views.xml',
        # 'report/hr_daily_attendance_report_template.xml',
        # 'wizard/hr_attendance_report_wizard_views.xml',
        # 'wizard/hr_daily_attendance_report_wizard_views.xml',
        # 'wizard/attendance_error_summary.xml',
        # 'report/gbs_hr_attendance_report_template.xml',
        # 'report/attendance_error_summary_report.xml',
        # 'wizard/employee_attendance_wizard.xml',
        # 'report/gbs_employee_attendance_report_template.xml',
        # 'report/attendance_summary_report_template.xml',
        # 'wizard/attendance_summary_report_wizard_view.xml',
        'wizard/job_card_wizard_view.xml',
    ],

    'summary': 'Generates check in and check out related report of employee(s)',
    'description': 'Generates check in and check out related report of employee(s)',
    'installable': True,
    'application': True,
}
