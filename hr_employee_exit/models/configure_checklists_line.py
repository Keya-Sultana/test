from odoo import models, fields, api, exceptions


class ConfigureChecklistsLine(models.Model):
    _name = "hr.exit.configure.checklists.line"
    _description = 'Configure Checklists Line'

    # Relational fields
    status_line_id = fields.Many2one('hr.checklist.status')
    checklist_item_id = fields.Many2one('hr.exit.checklist.item', domain=[('is_active', '=', True)],
                                        string='Checklist Item', required=True)
    checklist_type = fields.Many2one('hr.exit.checklist.type', ondelete='set null', store=True,
                                     related='checklist_item_id.checklist_type',
                                     string='Checklist Type')
    checklists_id = fields.Many2one('hr.exit.configure.checklists')
    responsible_department = fields.Many2one('hr.department', string='Responsible Department', store=True,
                                             compute='_checkApp')
    responsible_emp = fields.Many2one('hr.employee', string='Responsible User', store=True, compute='_checkApp')

    @api.constrains('checklists_id')
    def _checkApp(self):
        if self.checklists_id.responsible_userdepartment_id:
            self.responsible_department = self.checklists_id.responsible_userdepartment_id.id
        elif self.checklists_id.responsible_username_id:
            self.responsible_emp = self.checklists_id.responsible_username_id.id
        else:
            pass
