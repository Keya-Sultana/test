{
    'name': "Stock User Operating Unit",

    'summary': """
        Relational Module Of Stock and User""",

    'description': """
        By this moduel user can define his default location and also and give access able locations. 
    """,

    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'license': 'LGPL-3',

    'category': 'Inventory',
    'version': "1.0.0",

    'depends': ['stock_operating_unit'],

    'data': [
        'views/stock_users_views.xml',
    ],

}