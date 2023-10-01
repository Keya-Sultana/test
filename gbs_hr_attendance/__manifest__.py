{
    'name': 'HR Attendance',
    'version': "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'summary': 'This module handles request of HR Attendance',
    'description': "Complete HR Attendance Program",
    'depends': [
        # 'hr',
        'hr_attendance',
        'hr_operating_unit',
                # 'gbs_hr_package',
                # 'gbs_application_group',
        ],
    'data': [
        'views/hr_attendance_view.xml',
        'views/hr_emp_map_to_device.xml',
        # 'security/ir_rule.xml',
    ],
    'installable': True,
    'application': False,
}
