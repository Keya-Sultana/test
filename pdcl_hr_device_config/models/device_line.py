from odoo import models, fields
from odoo import api
import json


class DeviceLine(models.Model):
    _name = 'hr.attendance.device.line'
    _description = "Device Line"

    name = fields.Char(size=100, string='Name', required='True')
    sensor_id = fields.Char(string='Machine Number', size=5, required=True)

    """" Relational Fields """
    device_detail_id = fields.Many2one("hr.attendance.device.detail", string="Device Details", required=True, ondelete='cascade')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
        ('sensor_id_uniq', 'unique(sensor_id)', 'This Device ID is already in use'),
    ]

