# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Slack Connector Work Log',
    'version': '1.0',
    'category': 'Services/Timesheets',
    'summary': 'This module will send employee work log.',
    'sequence': 56,
    'depends': [
        'base',
        'analytic',
        'slack_connector',
    ],
    'data': [
        'views/company_view.xml',
        'views/slack_work_log_cron.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
