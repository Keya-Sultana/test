{
    'name': "Stock Issue Report",

    'summary': """
        Custom Report Of Issue Product""",

    'description': """
        By this report user can get the record of 
        issued product list by departmental and periodical.
    """,

    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",

    'category': 'Stock',
    'version': "1.0.0",
    'license': 'LGPL-3',

    'depends': [
        'stock_indent',
        # 'web.report_layout'
    ],

    'data': [
        'security/ir.model.access.csv',
        'report/stock_issue_report.xml',
        'wizard/stock_issue_wizard.xml',

    ],

}