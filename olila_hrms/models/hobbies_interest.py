
from random import randint

from odoo import fields, models


class EmployeeHobbiesInterests(models.Model):

    _name = "hr.hobbies.interests"
    _description = "Employee Hobbies and Interests"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
