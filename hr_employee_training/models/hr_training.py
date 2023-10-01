from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class HrTraining(models.Model):
    _name = 'hr.training'
    _inherit = ['mail.thread']
    _rec_name = 'code'
    _order = 'code desc'
    _description = 'Make Employees Training '

    TYPE = [
        ('functional', 'Functional'),
        ('technical', 'Technical'),
        ('other', 'Other')
    ]

    training_type = fields.Selection(
        selection=TYPE,
        string="Training Type1",
        index=True,
        tracking=True,
        required=True,
    )
    code = fields.Char('Code', required=True)
    type_id = fields.Many2one('hr.training.type', string="Training Type", required=True, tracking=True,)
    active = fields.Boolean('Active', default=True)
    skill_id = fields.Many2one('hr.skill', required=True, tracking=True,)


class HrTrainingType(models.Model):
    _name = 'hr.training.type'
    _inherit = ['mail.thread']
    _description = 'Make Employees Training Type '
    _order = "id"

    name = fields.Char('Training Type', required=True)

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['hr.training.type'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('This name is already existed')
