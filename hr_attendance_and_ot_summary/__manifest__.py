{
    'name': 'HR Attendance and Over Time (OT) Summary',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'HR Attendance',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'wizards/attendance_summary_wizard_views.xml',
        'views/attendance_summary_view.xml',
        # 'report/hr_attendance_summary_report_template.xml',
        'report/hr_attendance_summary_report_view.xml',

    ],
    
    'depends': [
        'hr_attendance',
        'hr_rostering',
        'gbs_hr_attendance_utility',
        'gbs_hr_attendance_grace_time',
        'hr_holidays',
        'hr_unpaid_holidays',
        'hr_holiday_year',
        # 'gbs_hr_employee',
        'gbs_hr_department_sequence',
        'gbs_hr_attendance_error_correction',
        'hr_employee_operating_unit',
        'hr_overtime_requisition',
        'hr_employee_seniority',
        'hr_attendance_settings',
        # 'hr_holiday_allowance',
        # 'web.report_layout'
    ],
    
    'description': 
    """This module will show attendance and over time summary at a glance of employees""",        
    'installable': True,
    'application': True,
}