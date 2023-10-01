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

from odoo import models, fields,api
class ChecklistItem(models.Model):
    _name = 'checklist.item'
    _rec_name = 'line_name'

    line_name = fields.Char(string='Name', required=True)
    user_id = fields.Many2one('res.users', string='Responsible User', required=True)


class ChecklistLine(models.Model):
    _name = 'checklist.line'

    _rec_name = 'name'

    name = fields.Char(string='Notes', required=True, default="/")
    checklist_item_id = fields.Many2one('checklist.item', string='Checklist Item', required=False)
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of sale quote lines.",
                              default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    checklist_id = fields.Many2one('orientation.checklist', string='Assessment Checklist')
    user_id = fields.Many2one('res.users', string='Responsible User', required=False)

    @api.onchange('checklist_item_id')
    def _onchange_user(self):
        if self.name:
            self.user_id = self.checklist_item_id.user_id.id
