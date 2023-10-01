{
    'name': 'HR Manual Attendance Request',
    "author": "Odoo Bangladesh",
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'HR Attendance',
    'version': "1.0.0",
    'description':
    """This module enables employee to request manual attendance""",
    'data': [
        'security/ir.model.access.csv',
        # 'security/hr_manual_attendance_security.xml',
        'views/hr_manual_attendance_view.xml',
        'views/manual_attendance_min_days_restriction_view.xml',
        'views/hr_manual_attendance_batches_view.xml',

    ],
    'depends': [
        'hr_attendance',
        'base_technical_features',
        # 'hr',
        # 'hr_holidays',
        # 'gbs_hr_attendance',
        # 'hr_holidays_multi_levels_approval',
    ],
    'installable': True,
    'application': True,
}