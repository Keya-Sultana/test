

{
    "name": "Operating Unit in Purchase Orders",
    "summary": "Adds the concecpt of operating unit (OU) in purchase order "
    "management",
    "version": "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    "category": "Purchase Management",
    "depends": ["stock_operating_unit", "purchase_stock"],
    "data": [
        "security/purchase_security.xml",
        "views/purchase_order_view.xml",
        "views/purchase_order_line_view.xml",
    ],
    "demo": ["demo/purchase_order_demo.xml"],
    "installable": True,
}
