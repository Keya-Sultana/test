from odoo import models, fields
# ai model missing v-15

class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    unpaid = fields.Boolean(
        'Unpaid',
        help="If checked, leave will considered as unpaid.", default=False
    )