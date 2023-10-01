from odoo import api,fields, models, _


class HrManualAttendanceMinDaysRestriction(models.TransientModel):
    _inherit = 'res.config.settings'
    # _name = 'hr.manual.attendance.min.days'
    # _description = 'Hr Manual Attendance Min Days Restriction'
    
    min_days_restriction = fields.Integer(string='Minimum Days Restriction', default=30)
    