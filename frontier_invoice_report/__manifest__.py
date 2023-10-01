{
    'name': 'Sale Pro-Forma Invoice Report',
    'version': "1.0.0",
    'author':  'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',
    'category': 'sale',
    'summary': 'sales',
    'description': "Report",
    'depends': [
        'sale',
        'amount_to_word_bd',
                ],
    'data': [
        'views/inherit_sale_order_view.xml',
        'reports/sale_report.xml',
        'reports/custom_external_layout_view.xml',
        'reports/proforma_invoice_report_templates.xml',
    ],
    'installable': True,
    'application': False,
}
