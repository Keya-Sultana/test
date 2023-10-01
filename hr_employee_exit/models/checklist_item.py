from odoo import models, fields, api, exceptions


class ChecklistItem(models.Model):
    _name = 'hr.exit.checklist.item'
    _inherit = ['mail.thread']
    _description = 'Employee Checklists Item'

    # Model Fields
    name = fields.Char(string='Item Name', size=100, required=True, help='Please enter name.',
                       tracking=True)
    description = fields.Text(string='Description', size=500, help='Please enter description.',
                              tracking=True)
    is_active = fields.Boolean(string='Active', default=True, tracking=True)

    # Relational Fields
    checklist_type = fields.Many2one('hr.exit.checklist.type',
                                     string='Checklist Type', domain=[('is_active', '=', True)],
                                     tracking=True,
                                     required=True, help='Please select checklist type.')
    # checklist_status_item_ids = fields.One2many('hr.checklist.status','checklist_status_item_id', string='Checklist
    # Status')

    checklist_item_id = fields.Many2one('hr.exit.configure.checklists.line')

    _sql_constraints = [
        ('_check_name_uniq', 'unique(name)', "Checklist item name already exists!"),
    ]
