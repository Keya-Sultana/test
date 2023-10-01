{
    'name': 'HR Holiday Report',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    'license': 'LGPL-3',
    'website': 'www.odoo.com.bd',
    'category': 'Human Resources',
    'summary': """""",
    'depends': [
        'hr_holidays',
                ],
    'data': [
        'security/ir.model.access.csv',
        "wizard/hr_holidays_summary_department_views.xml",
    ],
    'installable': True,
    'application': True,
}
