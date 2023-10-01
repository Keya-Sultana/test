
{
    'name': 'Slack Connector Check In Out Notification',
    'version': '0.1.0',
    'summary': 'This module will send employees check in out notification.',
    'category': 'Human Resources',
    'sequence': 55,
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': [
        'hr_attendance',
        'slack_connector',
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
