from odoo import models

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MlaContract(models.Model):
    _name = "hr.contract"
    _inherit = ["hr.contract", "multi.level.approval"]

    state = fields.Selection(selection_add=[('to approve', 'To Approve')])

    def action_confirm(self):
        for iterate in self:
            if iterate.pending_approver:
                iterate.state = 'to approve'
            else:
                raise ValidationError(_('Approval Chain is not set'))

    def action_reject(self):
        self.state = 'cancel'

    def write(self, vals):
        try:
            if self.state == 'draft' and vals['state'] == 'open':
                raise ValidationError(_('An Employee can\'t go to Running state without having approval'))
            else:
                res = super(MlaContract, self).write(vals)
        except KeyError:
            pass

    def new_approval_po(self):
        for po in self:
            pending_approver = po.next_pending_approver()

            if pending_approver:
                po.pending_approver = pending_approver
            else:
                po.pending_approver = False
                po.state = 'open'
