import base64

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class MultiLevelApproval(models.Model):
    _name = "multi.level.approval"
    _description = "Multilevel Approval"

    def _default_approver(self):
        mla_cat_obj = self.env["multi.level.approval.category"].search([('approval_model_id.model', '=', self._name)])
        if mla_cat_obj and mla_cat_obj.approver_ids and mla_cat_obj.approver_ids[0]:
            return mla_cat_obj.approver_ids[0].user_id.id

        return False

    def _compute_current_user_is_approver_or_not(self):
        for po in self:
            if po.pending_approver.id == self.env.user.id:
                po.current_user_is_approver_or_not = True

            else:
                po.current_user_is_approver_or_not = False

    pending_approver = fields.Many2one('res.users', string="Pending Approver", readonly=True,
                                       default=_default_approver)
    # pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
    #                                         related='pending_approver.user_id', related_sudo=True, store=True,
    #                                         readonly=True)
    current_user_is_approver_or_not = fields.Boolean(string='Current user is approver',
                                                     compute='_compute_current_user_is_approver_or_not')

    def next_pending_approver(self):
        mla_cat_obj = self.env["multi.level.approval.category"].search([('approval_model_id.model', '=', self._name)])

        # next_uid = mla_cat_obj.approver_ids.user_id.ids
        current_index = mla_cat_obj.approver_ids.user_id.ids.index(self.env.uid)
        if len(mla_cat_obj.approver_ids.user_id.ids) > current_index + 1:
            return mla_cat_obj.approver_ids.user_id.ids[current_index + 1]

        return False
