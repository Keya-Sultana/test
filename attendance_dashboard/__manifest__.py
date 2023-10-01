{
    'name': "Attendance Dashboard",
    'depends': [
        'gbs_hr_attendance_error_correction',
    ],
    'data': [
        'views/attendance_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'attendance_dashboard/static/src/scss/attendance.scss',
            'attendance_dashboard/static/src/js/attendance_dashboard.js',
        ],
        'web.assets_qweb': [
            'attendance_dashboard/static/src/xml/attendance_dashboard.xml',
        ],
    }
}