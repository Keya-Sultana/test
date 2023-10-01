{
    "name": "HR Employee Operating Unit",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'sequence': 101,
    "category": "Human Resources",
    "depends": ["hr",
                "operating_unit",
                ],
    "data": [
        "views/hr_views.xml",
        # "security/hr_emp_security.xml",
    ],

    'installable': True,
    'application': True,
}
