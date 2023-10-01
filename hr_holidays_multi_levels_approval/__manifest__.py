{
    "name": "Holidays multi levels approval",
    "version": "1.0.0",
    "author": "Odoo Bangladesh",
    "category": "Generic Modules/Human Resources",
    'website': 'www.odoo.com.bd',
    'images': ['static/description/banner.jpg'],
    'depends': ['hr', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/holidays.xml'
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

