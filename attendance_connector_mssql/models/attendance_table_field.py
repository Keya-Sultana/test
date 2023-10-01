from odoo import models, fields


class AttendanceTableMapping(models.Model):
    _name = 'attendance.table.field'
    _description = "Attendance Table Mapping"

    type_code = fields.Selection([
        ('employee_code', "Employee Mapping"),
        ('att_date', "Attendance Date"),
        ('att_time', "Attendance Time"),
        ('att_date_time', "Attendance DateTime"),
        ('IN_OUT', "IN / OUT"),
    ], string='Type', required=True)

    type_value = fields.Char(string='Code', size=20, required=True)

    """" Relational Fields """
    device_detail_id = fields.Many2one("hr.attendance.device.detail", string="Device Details", required=True, ondelete='cascade')





