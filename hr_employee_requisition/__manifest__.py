{
    'name': 'Employee / Manpower Requisition',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'summary': 'HR',
    'description': """""",
    'sequence': 4,
    'depends': [
                "hr_recruitment",
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/employee_requisition_views.xml',
        'views/employee_requisition_line_views.xml',
             ],
    'auto_install': False,
    'application': False,
    'installable': True,
}