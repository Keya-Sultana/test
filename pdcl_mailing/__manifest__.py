{
    "name": "Create Mailing Lists For PDCL",
    'license': 'LGPL-3',
    'version': "1.0.0",
    "category": "Generic Modules/Human Resources",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    "depends": ['base', "mass_mailing"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mail_list_select_view.xml",
    ],
    "installable": True,
}
