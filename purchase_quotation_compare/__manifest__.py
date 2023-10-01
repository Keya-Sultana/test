{
    'name': "Purchase Quotation Compare",

    'summary': """
        Generate Report Base on Purchase Quotation""",

    'description': """
        This module generate the report to compare the quotation vale based on PR.
          In this report user can see comparision of different quotation. 
    """,

    'author': "Odoo Bangladesh",
    'website': "www.odoo.com.bd",
    'license': 'LGPL-3',
    'category': 'Purchase',
    'version': "1.0.0",

    # any module necessary for this one to work correctly
    'depends': [
        'purchase_requisition',
        # 'web.report_layout',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/report_view.xml',
        'report/template_purchaserequisitions.xml',
    ],
}