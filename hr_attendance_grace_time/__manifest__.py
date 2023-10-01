{
    "name": "Attendance Grace Time",
    "summary": """Create Grace time for employee shifting""",
    "version": "1.0.0",
    "author": "Odoo Bangladesh",
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'Attendances',
    "depends": [
        'hr_attendance',
        'hr_operating_unit'
    ],
    "data": [
        "views/hr_attendance_grace_time_views.xml",
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True
}