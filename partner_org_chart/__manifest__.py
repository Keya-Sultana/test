{
    "name": "Partner Organization Chart",
    "summary": """Organization Chart Widget for Partner""",
    "description": """Organization Chart Widget for Partner""",
    "depends": ["base", "contacts"],
    "author": "Odoo Bangladesh",
    "website": "www.odoo.com.bd",
    "category": "Tools",
    "version": "1.0.0",
    "license": "LGPL-3",
    "data": [
        "views/partner_views.xml"
    ],
    'assets': {
        'web._assets_primary_variables': [
            'partner_org_chart/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'partner_org_chart/static/src/scss/partner_org_chart.scss',
            'partner_org_chart/static/src/js/partner_org_chart.js',
        ],
        'web.assets_qweb': [
            'partner_org_chart/static/src/xml/partner_org_chart.xml',
        ],
    },
    "application": True,
    "installable": True,
}
