
{
    "name": "Purchase order revisions",
    "version": "1.0.0",
    "category": "Purchase Management",
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
