{
    'name': 'HR Attendance Settings',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'sequence': 101,
    'summary': 'Customized settings for HR Attendance',
    'description': """
HR Attendance Settings
==========================

This application enables you to change the configurable part
You can manage:
---------------
* Attendance Summary
* Attendance Role
    """,
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': [
        'base',
        'base_setup',
        'hr_attendance',
    ],
    'data': [
        'data/settings_data.xml',
        # 'security/ir.model.access.csv',
        # 'views/hr_attendance_settings_views.xml',
        'views/inherit_res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
