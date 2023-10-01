# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import defaultdict
from datetime import datetime, date, time
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class PayslipBatchesSummaryWizard(models.TransientModel):
    _name = 'payslip.batches.summary.wizard'
    _description = 'Generate Payslip Batches Summary Report'

    start_date = fields.Date('Start Date', required=True,
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    end_date = fields.Date('End Date', required=True, default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    def process_report(self):
        if self.start_date.month != self.end_date.month:
            raise ValidationError(_("Start Date and End Date are not in the same month!"))

        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return self.env.ref('gbs_hr_payroll.action_payslip_batches_summary_report').report_action(None, data=data)
