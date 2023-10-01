{
    'name': 'Indent Management',
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'live_test_url': 'https://showcase.binaryquest.com',
    'website': "https://www.binaryquest.com",
    'version': "1.0.0",
    'license': 'OEEL-1',
    'category': 'Inventory',
    'description': """
Indent Management
===================
Usually big companies set-up and maintain internal requisition to be raised by Engineer, Plant Managers or Authorised Employees. Using Indent Management you can control the purchase and issue of material to employees within company warehouse.

- Purchase Indents
- Store purchase
- Capital Purchase
- Repairing Indents
- Project Costing
- Valuation
- etc.

Purchase Indents
++++++++++++++++++
When there is a need of specific materials or services, authorized employees or managers will create a Purchase Indent. He can specify required date, whether the indent is for store or capital, the urgency of materials etc. on indent.

While selecting the product, the system will automatically set the procure method based on the quantity on hand for the product. Once the indent is approved, an internal move has been generated. A purchase order will also be generated if the products are not in stock and to be purchased.


Repairing Indents
++++++++++++++++++
A store manager or will create a repairing indent when the product is needed to be sent for repairing. In case of repairing indent you will be able to select product to be repaired and service for repairing of the product.

A purchase order is generated for the service taken for the supplier who repairs the product, and an internal move has been created for the product to be moved for repairing.
    """,
    'depends': [
        'stock',
    ],
    'complexity': "normal",
    'images': [
        'static/description/banner.png',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/stock_indent_report.xml',
        'data/stock_indent_data.xml',
        'views/indent_type_views.xml',
        'views/inherited_product_category.xml',
        'views/stock_location_view.xml',
        'views/stock_indent_view.xml',
        'views/stock_indent_config_views.xml',
        'views/stock_users_views.xml',
        'views/my_stock_indent_view.xml',
        'views/inherited_product_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stock_indent/static/src/js/indent_dashboard.js',
        ],
        'web.assets_qweb': [
            'stock_indent/static/src/xml/indent_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
}
