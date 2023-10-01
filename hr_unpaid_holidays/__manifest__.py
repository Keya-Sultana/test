{
    'name': 'Unpaid Holidays',
    'version': "1.0.0",
    'sequence': 30,
    'category': 'Human Resources',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': ['hr_holidays'],
    'data': [
        # 'views/hr_holidays_status.xml',
    ],
    'installable': True,
    'application': False,
}
