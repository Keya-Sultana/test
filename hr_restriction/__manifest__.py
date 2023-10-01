{
    'name': 'HR Restriction',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category': 'hr',
    'version': "1.0.0",
    'license': 'LGPL-3',
    'description': " This module shows restriction on deletion of data ",
    'depends': [
        'hr', 'hr_skills',
    ],
    'data': [
        'data/security_view.xml',
    ],
    'installable': True,
    'application': True,
}
