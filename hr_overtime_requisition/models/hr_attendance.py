from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    ot_hours = fields.Float('OT Hours')
