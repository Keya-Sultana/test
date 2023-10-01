from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    exclude_public_holidays = fields.Boolean(
        string="Exclude Public Holidays",
        default=True,
        help=("If enabled, public holidays are skipped in leave days calculation."),
    )
