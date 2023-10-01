{
	'name': "Organization Department Hierarchy",
	'summary': """Dynamic display of your Department Organization""",
	'description': """Dynamic display of your Department Organization""",
	'website': 'www.odoo.com.bd',
	'author': "Odoo Bangladesh",
	'category': 'Human Resources',
	'version': "1.0.0",
	'license': 'LGPL-3',
	'depends': ['hr'],
	'data': [
		'views/org_chart_views.xml'
	],
	'assets': {
            'web.assets_backend': [
                'org_department_hierarchy/static/js/org_chart_department.js',
				'org_department_hierarchy/static/js/jquery_orgchart.js',
                'org_department_hierarchy/static/src/css/jquery_orgchart.css',
				'org_department_hierarchy/static/src/css/style.css',
            ],
            'web.assets_qweb': [
                'org_department_hierarchy/static/src/xml/org_chart_department.xml',
            ],
    },

	'installable': True,
	'application': True,
	'auto_install': False,
}
