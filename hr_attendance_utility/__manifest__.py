{
    'name': 'Attendance Utilities',
    'category': 'Attendances',
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'version': "1.0.0",
    'data': [
        "security/ir.model.access.csv",
    ],
    'depends':
        ['hr',
         'hr_rostering',
         'hr_holidays_public'
         ]
}
