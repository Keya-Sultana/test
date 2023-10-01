# Copyright 2019 Odoo TEAM CI
{
	'name': 'Url Access Restriction',
	'version': "1.0.0",
	'category': 'Web',
	'sequence': 0,
	'author': 'Odoo Bangladesh',
	'website': 'www.odoo.com.bd',
	'summary': 'Module Use of Url Access Restriction',
	'license': 'LGPL-3',
	'depends': ['web'],
	'assets': {
		'web.assets_backend': [
			'url_access_restriction/static/src/js/url_access_restriction.js',
		],
		'web.assets_qweb': [
			'url_access_restriction/static/src/xml/warning_message_page.xml',
		],
	},

	# 'images': [
	# 	'static/src/img/main_screenshot.png'
	# ],
	'data': [
		# 'views/url_access_restriction.xml',
	],
	# 'qweb': [
	# 	'static/src/xml/warning_message_page.xml',
	# ],
	'installable': True,
	'application': True
}
