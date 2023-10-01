# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    overlapping_approval = fields.Boolean(string='Overlapping Approval',
                                          config_parameter='multi_level_approval.overlapping_approval')

    required_approval = fields.Boolean(string='Required Approval',
                                       config_parameter='multi_level_approval.required_approval')
    conditional_approval = fields.Boolean(string='Conditional Approval',
                                          config_parameter='multi_level_approval.conditional_approval')
