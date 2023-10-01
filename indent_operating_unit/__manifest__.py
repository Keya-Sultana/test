{
    'name': 'Indent Operating Unit',
    'version': "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'sequence': 101,
    'summary': 'This module handles Indent Oparating Unit',
    'description': "Complete Indent Oparating Unit Program",
    'depends': [
        'stock_indent',
        'operating_unit',
    ],
    'data': [
        'views/oparating_unit_indent.xml',
    ],
    'installable': True,
    'application': True,
}