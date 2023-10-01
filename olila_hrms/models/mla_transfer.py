from odoo import models


class MlaTransfer(models.Model):
    _name = "hr.employee.transfer"
    _inherit = ["hr.employee.transfer", "multi.level.approval"]

    def new_approval_po(self):
        for po in self:
            pending_approver = po.next_pending_approver()

            if pending_approver:
                po.pending_approver = pending_approver
            else:
                po.pending_approver = False
                po.action_done()
