# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import models, fields, api, _


class MachineAttendance(models.Model):
    _name = 'machine.attendance'

    @api.constrains('employee_code', 'device_id', 'punching_time')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass

    employee_code = fields.Char(string='Employee Device Code', required=True)
    punching_time = fields.Char(string='Punching Time', required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    device_id = fields.Many2one('hr.attendance.device.detail', string='Biometric Device ID')
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    attendance_id = fields.Many2one("hr.attendance", string="Attendance Ref")
    state = fields.Selection([('0', 'Draft'),
                              ('1', 'Processed')], string='Status', required=True, default='0')
