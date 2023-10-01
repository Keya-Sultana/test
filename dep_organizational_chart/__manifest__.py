# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'Department Organizational Hierarchy',
    'version': '1.0.0',
    'summary': 'HR Department organizational chart',
    'description': 'HR Department organizational chart',
    'author': "Odoo Bangladesh",
    'category': 'Generic Modules/Human Resources',
    'website': 'www.odoo.com.bd',
    'depends': ['hr'],
    'data': [
        'views/show_employee_chart.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dep_organizational_chart/static/src/js/organizational_view.js',
            'dep_organizational_chart/static/src/scss/chart_view.scss',


        ],
        'web.assets_qweb': [
            'dep_organizational_chart/static/src/xml/chart_view.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
