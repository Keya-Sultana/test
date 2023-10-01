{
    'name': 'HR ManPower Requisition Multi Approval',
    'version': "1.0.0",
    "author": "Odoo Bangladesh",
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'summary': 'HR',
    'description': """
    
    """,
    'category': 'Human Resources',
    'sequence': 4,
    'depends': ["hr_manpower_requisition"],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_requisition_view.xml'
             ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

