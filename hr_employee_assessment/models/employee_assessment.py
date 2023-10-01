# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, _


class Assessment(models.Model):
    _name = 'employee.assessment'
    _description = "Employee Assessment"
    _inherit = 'mail.thread'

    assessment_request_id = fields.Many2one('employee.assessment.request', string='Assessment requests')
    assessment_user_id = fields.Many2one('res.users', string='Responsible User')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    line_ids = fields.One2many('assessment.line', 'employee_assessment_id', string='Assessment Lines')
    employee_name = fields.Many2one('hr.employee', string='Employee', related='assessment_request_id.employee_name')

    def confirm_request(self):
        for request in self:

            if request.state == 'draft':
                request.line_ids.state = 'complete'
        self.write({'state': "complete"})
