{
    "name": "HR Holidays Public",
    "version": "2.0.4",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    "category": "Human Resources",
    "summary": "Manage Public Holidays",
    "depends": ["hr_holidays", 'operating_unit',],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/hr_holidays_public_view.xml",
        "views/hr_leave_type.xml",
        "wizards/holidays_public_next_year_wizard.xml",
    ],
    "installable": True,
}
