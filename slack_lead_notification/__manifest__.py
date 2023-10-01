# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Slack Connector Lead Notification',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'This module will send lead notification.',
    'sequence': 56,
    'depends': [
        'crm',
        'slack_connector',
    ],
    'data': [
        'views/company_view.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
