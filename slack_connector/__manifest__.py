# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Bangladesh Limited
#    Copyright (C) 2017-TODAY Odoo Bangladesh (<http://www.odoo.com.bd>).

#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Slack Connector',
    'version': '1.0.0',
    'summary': 'This module will wish the employees on their work anniversary.',
    'category': 'Human Resources',
    'sequence': 55,
    'author': 'Odoo Bangladesh',
    'company': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/company_view.xml'],
    'test': [],
    'license': 'OEEL-1',
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
