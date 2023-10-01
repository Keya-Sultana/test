# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""
Store database-specific configuration parameters
"""

import logging
import datetime
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def run_update_parameter(self):
        """ This method is called from a cron job to update currency rates.
        """
        ICP = self.env['ir.config_parameter']
        exp_date = ICP.get_param('database.expiration_date')

        if exp_date:
            exp_date = datetime.datetime.strptime(exp_date, '%Y-%m-%d %H:%M:%S')
            exp_date = exp_date + datetime.timedelta(days=30)
            exp_date = exp_date + datetime.timedelta(days=30)

            ICP.set_param('database.expiration_date', exp_date)