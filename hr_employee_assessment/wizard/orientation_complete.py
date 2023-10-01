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

from odoo import api, fields, models, _


class AssessmentForceComplete(models.TransientModel):
    _name = 'assessment.force.complete'

    name = fields.Char()
    assessment_id = fields.Many2one('employee.assessment.request', string='Assessment')
    assessment_lines = fields.One2many('employee.assessment.request', string='assessment Lines', compute='pending_lines')

    @api.onchange('assessment_id')
    def pending_lines(self):
        pending = []

        for data in self.assessment_id.assessment_request:
            if data.state == 'new':
                pending.append(data.id)
        self.update({'assessment_lines': pending})

    def force_complete(self):
        for line in self.assessment_lines:
            if line.state != 'cancel':
                line.state = 'complete'
        self.assessment_id.write({'state': 'complete'})



