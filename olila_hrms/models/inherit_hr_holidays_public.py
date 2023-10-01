from odoo import api, fields, models


class HrHolidaysPublic(models.Model):
    _inherit = "hr.holidays.public"

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit')

    def _check_year_one(self):
        return True