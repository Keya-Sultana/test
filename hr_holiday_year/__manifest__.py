{
    'name': 'HR Holiday Year',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    'license': 'LGPL-3',
    'website': 'www.odoo.com.bd',
    'category': 'Human Resources',
    'summary': """Computes the actual leave days 
               considering rest days and public holidays""",
    'depends': [
        'hr_holidays',
        'date_range',
                ],
    'data': [
        'views/hr_holidays_view.xml',
        'views/date_range_view.xml',
    ],
    'installable': True,
    'application': True,
}
