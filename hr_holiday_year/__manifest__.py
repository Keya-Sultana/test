{
    'name': 'HR Holiday Year',
    'version': "14.0.1.0.0",
    "author": "Odoo Bangladesh",
    "website": "",
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
