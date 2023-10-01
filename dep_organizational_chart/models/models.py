# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Yadhu K (<https://www.cybrosys.com>)
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

from odoo import models, fields, api


class OrganizationalChart(models.Model):
    _name = 'hr.organizational.chart'
    _description = "HR Organizational Chart"

    @api.model
    def get_employee_data(self, dep_id):
        parent_emp = self.env['hr.department'].search([('id', '=', str(dep_id))])
        data = {
            'name': parent_emp.name,
            # 'title': self._get_position(parent_emp),
            'children': [],
            # 'office': self._get_image(parent_emp),
        }
        departments = self.env['hr.department'].search([('parent_id', '=', parent_emp.id)])
        for department in departments:
            data['children'].append(self.get_children(department, 'middle-level'))

        return {'values': data}

    @api.model
    def get_children(self, emp, style=False):
        data = []
        emp_data = {'name': emp.name,}
        childrens = self.env['hr.department'].search([('parent_id', '=', emp.id)])
        for child in childrens:
            sub_child = self.env['hr.department'].search([('parent_id', '=', child.id)])
            next_style = self._get_style(style)
            if not sub_child:
                data.append({'name': child.name, 'className': next_style,
                             })
            else:
                data.append(self.get_children(child, next_style))

        if childrens:
            emp_data['children'] = data
        if style:
            emp_data['className'] = style

        return emp_data

    def _get_style(self, last_style):
        if last_style == 'middle-level':
            return 'product-dept'
        if last_style == 'product-dept':
            return 'rd-dept'
        if last_style == 'rd-dept':
            return 'pipeline1'
        if last_style == 'pipeline1':
            return 'frontend1'

        return 'middle-level'

    def _get_image(self, emp):
        image_path = """<img src='/web/image/hr.employee.public/""" + str(emp.id) + """/image_1024/' id='""" + str(
            emp.id) + """'/>"""
        return image_path

    def _get_position(self, emp):
        if emp.sudo().job_id:
            return emp.sudo().job_id.name
        return ""
