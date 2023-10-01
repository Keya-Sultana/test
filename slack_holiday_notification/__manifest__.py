
{
    'name': 'Slack Connector Holidays Notification',
    'version': '0.1.0',
    'summary': 'This module will send employee holidays notification.',
    'category': 'Human Resources',
    'sequence': 56,
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': [
        'hr_holidays',
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
