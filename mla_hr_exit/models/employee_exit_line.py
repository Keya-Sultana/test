from odoo import models


class ExitRequest(models.Model):
    _name = "hr.emp.exit.req"
    _inherit = ["hr.emp.exit.req", "multi.level.approval"]

    def new_approval_po(self):
        for po in self:
            pending_approver = po.next_pending_approver()

            if pending_approver:
                po.pending_approver=pending_approver
            else:
                po.pending_approver = False
                po.exit_done()
