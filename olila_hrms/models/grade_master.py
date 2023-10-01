from random import randint

from odoo import fields, models


class GradeMaster(models.Model):
    _name = "grade.master"
    _description = "Grade Master"

    name = fields.Char(string="Grade Name", required=True)
    code = fields.Char(string="Grade Code", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class TAMaster(models.Model):
    _name = "ta.master"

    name = fields.Char('Name')
