from odoo import api, models, fields


class ApprovalTypeApprover(models.Model):
    _name = "mla.category.approver"
    _description = "Multilevel Category Approval"

    category_id = fields.Many2one('multi.level.approval.category', string='Approval Type', readonly=False, index=False,
                                  store=True)
    company_id = fields.Many2one('res.company', string='company', readonly=True, index=False, store=False)
    display_name = fields.Char(string='Display Name', index=False, store=False, readonly=True)
    existing_user_ids = fields.Many2many('res.users', string='Existing User', index=False, store=False, readonly=True)
    required = fields.Boolean(string='Required', index=False, store=True, readonly=False)
    user_id = fields.Many2one('res.users', string='User', index=False, store=True, readonly=False)
