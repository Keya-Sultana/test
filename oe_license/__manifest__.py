# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Enterprise License',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
Odoo Enterprise License.
===========================

This module extend the Enterprise License.
        """,
    'depends': ['web'],
    'auto_install': True,
    'data': [
        'views/service_cron_data.xml',
    ],
    'qweb': [],
    'license': 'OEEL-1',
}
