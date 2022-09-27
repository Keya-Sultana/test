{
    'name': 'Product Sales Pricelist',
    'version': '10.1.0.0',
    'category': 'sales',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'summary': "This module handles request of changing Product Sale Price",
    'depends': [
        'gbs_application_group',
        'sale',
        'product',
        'sales_team',
        'account',
        'stock',
        'report_layout',
        'product_variant_sale_price',
        'terms_setup',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sales_price_security.xml',
        'wizards/sale_price_change_wizard_view.xml',
        'views/sale_price_change_history.xml',
        'views/sale_price_change_view.xml',
        'views/inherited_products_view.xml',
        'views/product_packaging_mode_view.xml',
        'report/change_product_price_report.xml',
        'views/ir_cron.xml',
        'views/product_variants_price_history_view.xml',
        'views/inherit_partner_view.xml',
        'views/inherit_product_product.xml',
    ],
    'installable': True,
    'application': False,
}
