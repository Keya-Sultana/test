
{
    "name": "Bquick Biometric Device Integration",
    'version': '1.0.0',
    'license': 'LGPL-3',
    'summary': """Integrating Biometric Device (Model: ZKteco uFace 202) With HR Attendance (Face + Thumb)""",
    'description': """This module integrates Odoo with the biometric device(Model: ZKteco uFace 202),odoo15,odoo,hr,attendance""",
    'category': 'Generic Modules/Human Resources',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': [
        'hr_attendance',
        'hr_zk_attendance',
        'digest'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_view.xml',
        'data/email_template_view.xml',
        'views/res_config_settings_views.xml',
        'views/inherit_zk_machine_attendance_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
