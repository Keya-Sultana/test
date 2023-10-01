from odoo import api, fields, models, _


class HRAttendanceConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'HR Attendance Config Settings'

    def _get_default(self):
        query = """select late_salary_deduction_rule from res_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        deduction_rule_value = self._cr.fetchone()
        if deduction_rule_value:
            return deduction_rule_value[0]

    late_salary_deduction_rule = fields.Integer(default=_get_default)

    def _get_time_duration(self):
        query = """select time_duration from res_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        param_value = self._cr.fetchone()
        if param_value:
            return param_value[0]

    time_duration = fields.Integer(default=_get_time_duration)

    def _get_server_url(self):
        query = """select server_url from res_config_settings order by id desc limit 1"""
        self._cr.execute(query, tuple([]))
        url_value = self._cr.fetchone()
        if url_value:
            return url_value[0]

    server_url = fields.Char(default=_get_server_url)

    def set_values(self):
        super(HRAttendanceConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('hr_attendance_settings.late_salary_deduction_rule',
                                                         self.late_salary_deduction_rule)
        self.env['ir.config_parameter'].sudo().set_param('hr_attendance_settings.time_duration',
                                                         self.time_duration)
        self.env['ir.config_parameter'].sudo().set_param('hr_attendance_settings.server_url',
                                                         self.server_url)
        company = self.env.company
        for rec in company:
            rec.write({'late_salary_deduction_rule': self.late_salary_deduction_rule,
                       'time_duration': self.time_duration,
                       'server_url': self.server_url,
                       })


class ResCompany(models.Model):
    _inherit = 'res.company'

    late_salary_deduction_rule = fields.Integer(string='Monthly Attendance Rule')
    time_duration = fields.Integer(string='Attendance Device In/Out Rule')
    server_url = fields.Char(string='Server Base URL')
