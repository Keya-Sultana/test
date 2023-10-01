from odoo import models, fields
from odoo import api
import json


class DeviceLineDetail(models.Model):
    _name = 'hr.attendance.device.line.details'
    _description = "Device Line Detail"

    type_code = fields.Selection([
        ('IN', "IN"),
        ('OUT', "OUT"),
        ('IN_RFID', "IN_RFID"),
    ], string='Type', required=True)

    type_value = fields.Char(string='Code', size=5, required=True)

    """" Relational Fields """
    device_line_id = fields.Many2one("hr.attendance.device.detail", string="Device Details", required=True, ondelete='cascade')





