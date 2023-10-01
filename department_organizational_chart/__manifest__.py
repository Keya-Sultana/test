{
    "name": "Department Organizational Chart",
    "summary": """Organization Chart Widget for Department""",
    "description": """Organization Chart Widget for Department""",
    "depends": ["base", "hr"],
    "author": "Odoo Bangladesh",
    "website": "www.odoo.com.bd",
    "category": "Tools",
    "version": "1.0.0",
    "license": "LGPL-3",
    "data": [
        "views/department_views.xml",
        'views/org_chart_views.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [
            'department_organizational_chart/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'department_organizational_chart/static/src/scss/depart_org_chart.scss',
            'department_organizational_chart/static/src/js/depart_org_chart.js',
            'department_organizational_chart/static/js/org_chart_department.js',
            'department_organizational_chart/static/js/jquery_orgchart.js',
            'department_organizational_chart/static/src/css/jquery_orgchart.css',
            'department_organizational_chart/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            'department_organizational_chart/static/src/xml/depart_org_chart.xml',
            'department_organizational_chart/static/src/xml/org_chart_department.xml'
        ],
    },
    "application": True,
    "installable": True,
}
