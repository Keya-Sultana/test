{
    "name": "Employee ID",
    "version": "1.0.0",
    'license': 'LGPL-3',
    "category": "Generic Modules/Human Resources",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    "depends": ["hr"],
    "data": [
        "data/hr_employee_sequence.xml",
        "views/hr_employee_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
