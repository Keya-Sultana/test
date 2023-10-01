from odoo import models, fields, _


class AssessmentType(models.Model):
    _name = 'assessment.type'
    _description = "Assessment Type"
    _inherit = 'mail.thread'
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True,
                            help="Set active to false to hide the Assessment Checklist without removing it.")
