{
    'name': 'Stellar Biometric Device Integration',
    'version': '1.0.0',
    'summary': """Integrating Biometric Device With HR Attendance (Thumb)""",
    'description': 'This module integrates Odoo with the biometric device(Model: Stellar)',
    'category': 'Generic Modules/Human Resources',
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': ['biometric_device_base', 'hr_attendance'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stellar_machine_view.xml',
        # 'views/zk_machine_attendance_view.xml',
        # 'data/download_data.xml'

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
