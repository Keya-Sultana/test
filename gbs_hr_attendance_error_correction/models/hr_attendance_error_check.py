from odoo import models, fields
from odoo import api


class AttendanceCheckError(models.Model):
    _inherit = 'hr.attendance'
    _order = "id"

    has_error = fields.Boolean(default=False, string='has_error', compute='onchange_attendance_data', store=True)
    check_in = fields.Datetime(string="Check In", required=False)
    duty_date = fields.Date(string='Duty Date', required=False)

    @api.depends('check_in', 'check_out')
    def onchange_attendance_data(self):
        for att in self:
            # if (att.check_in is None or False) or (att.check_out is None or False):
            if att.check_in == False or att.check_out == False:
                att.has_error = True

            elif att.check_out and att.check_in and att.check_out < att.check_in:
                att.has_error = True

            else:
                att.has_error = False
