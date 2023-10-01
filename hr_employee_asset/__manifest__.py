
{
    'name': 'Employee Asset Management',
    'version': '1.0',
    'author': 'Odoo Bangladesh',
    'summary': 'HR',
    'description': """
    
    """,
    'category': 'Human Resources',
    'sequence': 4,
    'website': '',
    'depends': [
        'hr',
        'hr_operating_unit',
        "mrp_maintenance",
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/asset_replacement_wizard_view.xml',
        "views/asset_allocation_request_views.xml",
        "views/asset_replacement_request_view.xml",
        'views/employee_asset_view.xml',
        'views/hr_employee_views.xml',
        # 'views/maintenance_views.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

