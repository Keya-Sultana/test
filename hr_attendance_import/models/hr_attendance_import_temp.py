from odoo import api, fields, models


class HrAttendanceImportLine(models.Model):
    _name = 'hr.attendance.import.temp'
    _description = "Hr Attendance Import Line"
    
    employee_code = fields.Char(string='Employee Code')
    check_in = fields.Char(string='Check In')
    check_out = fields.Char(string='Check Out')
    import_id = fields.Many2one('hr.attendance.import', 'id', ondelete='cascade')
    
    