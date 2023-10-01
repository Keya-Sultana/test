from odoo import api, fields, models, _


class ZKAttendanceConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'ZK Attendance Config Settings'

    attendance_receive_date = fields.Datetime(string='Receive attendance from this datetime',
                                              config_parameter='bquick_zk_attendance.attendance_receive_date')

    def set_values(self):
        super(ZKAttendanceConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bquick_zk_attendance.attendance_receive_date',
                                                         self.attendance_receive_date)
        company = self.env.company
        # zk_obj = self.env['zk.machine'].search([])
        for rec in company:
            rec.write({'attendance_receive_date': self.attendance_receive_date})


class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_receive_date = fields.Datetime(string='Attendance receive datetime')
