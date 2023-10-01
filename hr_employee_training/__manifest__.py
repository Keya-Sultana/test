
{
    'name': 'Employee Training Management',
    'version': '1.0',
    'author': 'Odoo Bangladesh',
    'summary': 'HR',
    'description': """
    
    """,
    'category': 'Human Resources',
    'sequence': 4,
    'website': '',
    'depends': [
        'hr', 'hr_skills',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/training_by_employees_views.xml',
        'views/hr_training_type.xml',
        "views/hr_training_views.xml",
        "views/hr_training_program_views.xml",
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}

