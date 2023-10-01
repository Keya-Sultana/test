from odoo import models


class SalesOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "multi.level.approval"]

    def new_approval_so(self):
        for so in self:
            pending_approver = so.next_pending_approver()

            if pending_approver:
                so.pending_approver=pending_approver
            else:
                so.pending_approver = False
                so.action_confirm()
