from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Many2one('biometric.base.device', string='Device')

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        return
