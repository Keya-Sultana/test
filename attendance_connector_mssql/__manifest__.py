{
    'name': 'Attendance Connector MSSQL',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'HR Attendance',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'description':
    """This module will connect to attendance devices""",
    'data': [
        'data/ir_cron.xml',
        'views/device_configuration_view.xml',
        'views/machine_attendance_view.xml',
        'security/ir.model.access.csv',
        'wizard/success_msg.xml',
    ],
    'depends': [
        'hr_attendance',
        # 'hr_attendance_import',
        "operating_unit",
        "hr_attendance_utility",
        "gbs_hr_attendance",
        "hr_attendance_settings",
        "hr_attendance_error_correction",
        "sh_message",
    ],
    'installable': True,
    'application': True,
}
