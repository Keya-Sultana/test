from odoo import api, models, fields


class ApprovalRule(models.Model):
    _name = "mla.rule.approver"
    _description = "Multilevel Rule Approver"

    category_id = fields.Many2one('multi.level.approval.rule', string='Approvers', readonly=False, index=False,
                                  store=True)
    company_id = fields.Many2one('res.company', string='company', readonly=True, index=False, store=False)
    display_name = fields.Char(string='Display Name', index=False, store=False, readonly=True)
    existing_user_ids = fields.Many2many('res.users', string='Existing User', index=False, store=False, readonly=True)
    required = fields.Boolean(string='Required', index=False, store=True, readonly=False)
    user_id = fields.Many2one('res.users', string='User', index=False, store=True, readonly=False, required=True)
    skip = fields.Boolean(string='Skip', index=False, store=True, readonly=False)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    log = fields.Char('Type of approval procedure')
    transfer_approvation = fields.Boolean(string='Transfer Approval', index=False, store=True, readonly=False)
    transfer_user = fields.Many2one('res.users', string='Transfer User', index=False, store=True, readonly=False)
    approval_type = fields.Selection([
        ('user', 'User'),
        ('department', 'Department')], string="Approval Type")

    # department_id = fields.Many2one('hr.department', string='Department')
    #
    # @api.onchange('approval_type', 'department_id')
    # def _onchange_approval_type(self):
    #     if self.approval_type == 'department' and self.department_id:
    #         return {'domain': {'user_id': [('id', 'in', self.department_id.member_ids.user_id.ids)]}}
    #     else:
    #         return {'domain': {'user_id': []}}

    @api.model_create_multi
    def create(self, vals_list):
        temp_list = []
        for index, vals in enumerate(vals_list):
            if vals.get('approval_type') == 'department' and vals.get('department_id'):
                department = self.env['hr.department'].browse(vals['department_id'])
                manager_ids = department.manager_id.user_id.id
                temp_val = {'index': index,
                            'data': {'approval_type': 'user', 'category_id': vals['category_id'],
                                     'department_id': False,
                                     'end_date': False,
                                     'required': False, 'skip': False, 'start_date': False,
                                     'transfer_approvation': False,
                                     'transfer_user': False, 'user_id': manager_ids}}

                temp_list.append(temp_val)

        if temp_list:
            for i in temp_list:
                vals_list.insert(i['index'], i['data'])

        return super(ApprovalRule, self).create(vals_list)


class ResUserTransferApprovation(models.Model):
    _inherit = ["res.users"]
    transfer_approvation = fields.Boolean(string='Transfer Approval', index=False, store=True, readonly=False)
    transfer_user = fields.Many2one('res.users', string='Transfer User', index=False, store=True, readonly=False)
    start_date = fields.Datetime(string='Start Date For Transfer Approval')
    end_date = fields.Datetime(string='End Date For Transfer Approval')

    @api.onchange('transfer_approvation', 'transfer_user', 'start_date', 'end_date')
    def update_approval_approvers(self):
        if self.transfer_approvation:
            approver = self.env['mla.rule.approver'].search([('user_id', '=', self.user_ids.ids[0])])
            if approver:
                approver.write({
                    'transfer_approvation': self.transfer_approvation,
                    'transfer_user': self.transfer_user.id,
                    'start_date': self.start_date,
                    'end_date': self.end_date,

                })
