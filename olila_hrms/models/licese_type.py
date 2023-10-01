
from random import randint

from odoo import fields, models


class LicenseType(models.Model):

    _name = "license.type"
    _description = "License Type"

    name = fields.Char(string="License Name", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
