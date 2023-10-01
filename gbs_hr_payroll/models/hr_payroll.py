import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import babel
from odoo import api, fields, models, tools, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        # result = super(HrPayslip, self).onchange_employee()
        date_from = self.date_from
        if date_from:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))

            locale = self.env.context.get('lang') or 'en_US'
            self.write({'name': _('Salary Slip of %s for %s') % (self.employee_id.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))})
        return
