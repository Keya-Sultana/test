from odoo import models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "multi.level.approval"]

    def new_approval_po(self):
        for po in self:
            pending_approver = po.next_pending_approver()

            if pending_approver:
                po.pending_approver = pending_approver
            else:
                po.pending_approver = False
                po.button_confirm()

    def _compute_current_user_is_approver_or_not(self):
        super(PurchaseOrder, self)._compute_current_user_is_approver_or_not()
        for order in self:
            if not order.current_user_is_approver_or_not:
                if self.env.ref("mla_purchase.group_purchase_head") in self.env.user.groups_id:
                    order.current_user_is_approver_or_not = True

