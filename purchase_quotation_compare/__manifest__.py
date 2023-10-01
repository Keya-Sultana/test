# -*- coding: utf-8 -*-
{
    'name': "Purchase Quotation Comparison",

    'summary': """
        Generate comparison report based on Purchase Quotation""",

    'description': """
        This module generate the report to compare the quotation vale based on Purchase Requisition.
          In this report user can see comparison of different quotation. 
    """,

    'author': "Odoo Bangladesh",
    'website': "http://odoo.com.bd",

    'category': 'Purchase',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_requisition'],

    # always loaded
    'data': [
        'views/report_view.xml',
        'report/template_purchaserequisitions.xml',
    ],
}