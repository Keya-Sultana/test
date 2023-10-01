from odoo import models


class MlaIncidentRaise(models.Model):
    _name = "incident.raise"
    _inherit = ["incident.raise", "multi.level.approval"]

    def new_approval_po(self):
        for po in self:
            pending_approver = po.next_pending_approver()

            if pending_approver:
                po.pending_approver = pending_approver
            else:
                po.pending_approver = False
                po.action_done()
