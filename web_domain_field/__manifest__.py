
{
    "name": "Web Domain Field",
    "summary": """
        Use computed field as domain""",
    "version": "1.0.0",
    "license": "LGPL-3",
    "author": "Odoo Bangladesh",
    "website": "www.odoo.com.bd",
    "depends": ["web"],
    "data": [
        # "views/web_domain_field.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'web_domain_field/static/lib/js/pyeval.js',
        ],
    },
    "installable": True,
}
