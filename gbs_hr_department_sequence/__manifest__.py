
{
    "name": "GBS HR Department Sequence",
    'sequence': 99,
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'version': "1.0.0",
    "category": "Human Resources",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_department_view.xml",
    ],
    'installable': True,
    'application': True
}
