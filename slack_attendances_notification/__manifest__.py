
{
    'name': 'Slack Connector Attendances Notification',
    'version': '0.1.0',
    'summary': 'This module will send employees attendance notification.',
    'category': 'Human Resources',
    'sequence': 55,
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': [
        'pdcl_hr_device_config',
        'slack_connector',
        'gbs_hr_attendance_report',
        ],
    'data': [
        'views/company_view.xml'
        ],
    'test': [],
    'license': 'OEEL-1',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
