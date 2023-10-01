{
    'name': 'HR Attendance Error Correction',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'HR Attendance',
    'license': 'LGPL-3',
    'version': "1.0.0",
    'data': [
        'security/ir.model.access.csv',
        'wizards/hr_attendance_error_wizard_view.xml',
        'views/hr_attendance_error_view.xml'
    ],
    'depends': [
        'hr',
        'hr_attendance',
        'gbs_hr_attendance',
        ],
    'summary': 'HR attendance error data correction process.',
    'description':
    """This module provides the way to correct the error of attendance data.""",
    'installable': True,
    'application': True,
}