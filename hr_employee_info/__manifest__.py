{
    "name": "Employee Personal Info",
    "version": "1.0.0",
    'license': 'LGPL-3',
    "category": "Generic Modules/Human Resources",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    "depends": ["hr", "hr_family"],
    "data": [
        'security/ir.model.access.csv',
        "views/hobbies_interest_view.xml",
        "views/inherit_hr_employee_view.xml",
    ],
    "installable": True,
}
