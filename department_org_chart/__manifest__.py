{
    "name": "Department Organization Chart",
    "summary": """Organization Chart Widget for Department""",
    "description": """Organization Chart Widget for Department""",
    "depends": ["base", "hr"],
    "author": "Odoo Bangladesh",
    "website": "www.odoo.com.bd",
    "category": "Tools",
    "version": "1.0.0",
    "license": "LGPL-3",
    "data": [
        "views/department_views.xml"
    ],
    'assets': {
        'web._assets_primary_variables': [
            'department_org_chart/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'department_org_chart/static/src/scss/depart_org_chart.scss',
            'department_org_chart/static/src/js/depart_org_chart.js',
        ],
        'web.assets_qweb': [
            'department_org_chart/static/src/xml/depart_org_chart.xml',
        ],
    },
    "application": True,
    "installable": True,
}
