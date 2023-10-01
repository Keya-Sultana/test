import base64

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource


class MultiLevelApproval(models.AbstractModel):
    _name = "multi.level.approval"
    _description = "Multilevel Approval"

    def _default_approver(self):
        mla_rule_obj = self.env["multi.level.approval.rule"].search([('approval_model_id.model', '=', self._name)])
        if mla_rule_obj and mla_rule_obj.approver_ids and mla_rule_obj.approver_ids[0]:
            return mla_rule_obj.approver_ids[0].user_id.id

        return False

    def mla_approve_actions(self):
        mla_rule_obj = self.env["multi.level.approval.rule"].search([('approval_model_id.model', '=', self._name)])
        method_name = self.env.context.get('approve_method')

        if self.approver_line_ids:
            for iterate in self.approver_line_ids:

                if self.env.uid == iterate.user_id.id:
                    iterate.is_approved = True
                    iterate.approve_by_user_id = self.env.uid
                    pending_approver = self.next_pending_approver()

                    if pending_approver:
                        ###checking approval minimum with approved count
                        if len(self.approver_line_ids.filtered(
                                lambda x: x.is_approved)) == mla_rule_obj.approval_minimum:
                            self.pending_approver = False
                            if method_name:
                                approve_method = getattr(self, method_name, None)
                                if callable(approve_method):
                                    approve_method()
                                   

                        else:
                            self.pending_approver = pending_approver
                           
                    else:
                        self.pending_approver = False
                        if method_name:
                            approve_method = getattr(self, method_name, None)
                            if callable(approve_method):
                                approve_method()
                               
                ###checking user not in approval chain but user is in transfer approval
                elif self.env.uid == iterate.transfer_user.id:
                    iterate.approve_by_user_id = self.env.uid
                    iterate.is_approved = True
                    iterate.log = 'Approved By transfer approval procedure'
                    pending_approver = self.next_pending_approver()

                    if pending_approver:
                        self.pending_approver = pending_approver
                    else:
                        self.pending_approver = False
                        if method_name:
                            approve_method = getattr(self, method_name, None)
                            if callable(approve_method):
                                approve_method()
                               

        else:
            if method_name:
                approve_method = getattr(self, method_name, None)
                if callable(approve_method):
                    approve_method()
                   

        if self.pending_approver:
            self.env['mail.message'].create({
                'date': fields.Datetime.now(),
                'model': self._name,
                'res_id': self.id,
                'author_id': self.env.user.partner_id.id,
                'body': 'Approved by ' + self.env.user.partner_id.name,
                'message_type': 'notification',
                'is_internal': True
            })

    def _compute_current_user_is_approver_or_not(self):
        mla_rule_obj = self.env["multi.level.approval.rule"].search([('approval_model_id.model', '=', self._name)])

        for record in self:
            if not mla_rule_obj:
                self.current_user_is_approver_or_not = True
                return
            ### normal chain of approval
            if record.pending_approver.id == self.env.user.id:
                record.current_user_is_approver_or_not = True
                return
            else:
                if record.pending_approver:
                    am_i_already_approved = len(record.approver_line_ids.filtered(
                        lambda x: x.is_approved and x.user_id.id == self.env.uid)) or False

                    if am_i_already_approved:
                        record.current_user_is_approver_or_not = False
                        return
                    approve_count = len(record.approver_line_ids.filtered(lambda x: x.is_approved))

                    for line in record.approver_line_ids:
                        ### Checking is the pending approver is required or not
                        ### If pending approver is required, then return False

                        check_required = 0
                        if self.env.uid in mla_rule_obj.approver_ids.user_id.ids:
                            check_required = len(record.approver_line_ids.filtered(
                                lambda x: mla_rule_obj.approver_ids.user_id.ids.index(
                                    x.user_id.id) < mla_rule_obj.approver_ids.user_id.ids.index(
                                    self.env.uid) and x.required and x.is_approved == False))

                        if check_required > 0:
                            record.current_user_is_approver_or_not = False
                            return
                        else:
                            allow_overlap = len(mla_rule_obj.approver_ids.user_id.ids) - (
                                    mla_rule_obj.approval_minimum - approve_count)

                            try:
                                current_user_index = mla_rule_obj.approver_ids.user_id.ids.index(self.env.uid) + 1
                            except ValueError:
                                ###checking transfer_user_already_approved_or_not
                                transfer_user_approved = (record.approver_line_ids.filtered(
                                    lambda x: x.is_approved and x.approve_by_user_id.id == self.env.uid)) or False
                                if transfer_user_approved:
                                    record.current_user_is_approver_or_not = False
                                    return
                                else:

                                    try:
                                        ###checking logged-in user is in transfer_approval list
                                        if len(record.approver_line_ids.filtered(
                                                lambda x: x.transfer_approvation and x.transfer_user.id == self.env.uid)):

                                            current_user_index = mla_rule_obj.approver_ids.user_id.ids.index(
                                                record.approver_line_ids.filtered(
                                                    lambda x: x.transfer_user.id).user_id.id) + 1

                                        else:
                                            record.current_user_is_approver_or_not = False
                                            return

                                    except ValueError:
                                        record.current_user_is_approver_or_not = False
                                        return

                                    ##checking user is in transfer_approval or not
                                    check_trans_approval_user = len(record.approver_line_ids.filtered(
                                        lambda x: x.transfer_approvation and x.user_id.id ==
                                                  mla_rule_obj.approver_ids.user_id.ids[
                                                      current_user_index - 1] and x.start_date <= fields.Datetime.now() <= x.end_date))
                                    if check_trans_approval_user and allow_overlap > 0:
                                        pending_approver_index = mla_rule_obj.approver_ids.user_id.ids.index(
                                            record.pending_approver.id) + 1
                                        if (current_user_index - pending_approver_index) <= allow_overlap:
                                            record.current_user_is_approver_or_not = True
                                            return
                                        else:
                                            record.current_user_is_approver_or_not = False
                                            return

                                    if not check_trans_approval_user:
                                        record.current_user_is_approver_or_not = False
                                        return

                            pending_approver_index = mla_rule_obj.approver_ids.user_id.ids.index(
                                record.pending_approver.id) + 1

                            if allow_overlap > 0:
                                if (current_user_index - pending_approver_index) <= allow_overlap:
                                    record.current_user_is_approver_or_not = True
                                    return
                                else:
                                    record.current_user_is_approver_or_not = False
                                    return
                            else:
                                record.current_user_is_approver_or_not = False

                                return

                else:
                    record.current_user_is_approver_or_not = True

    pending_approver = fields.Many2one('res.users', string="Pending Approver", readonly=True,
                                       default=_default_approver)

    current_user_is_approver_or_not = fields.Boolean(string='Current user is approver',
                                                     compute='_compute_current_user_is_approver_or_not')
    approver_line_ids = fields.One2many(
        'mla.approver', 'res_id', string='Approver Lines',
        auto_join=True)

    def next_pending_approver(self):
        mla_rule_obj = self.env["multi.level.approval.rule"].search([('approval_model_id.model', '=', self._name)])
        if self.env.uid not in mla_rule_obj.approver_ids.user_id.ids:
            current_index = mla_rule_obj.approver_ids.user_id.ids.index(
                self.approver_line_ids.filtered(lambda x: x.transfer_user.id).user_id.id) + 1

        else:
            current_index = mla_rule_obj.approver_ids.user_id.ids.index(self.env.uid) + 1

        if len(mla_rule_obj.approver_ids.user_id.ids) > current_index:

            if mla_rule_obj.approver_ids.user_id.ids[current_index]:

                for record in self:

                    for line in record.approver_line_ids:
                        ### checking skip procedure
                        if line.user_id.id == mla_rule_obj.approver_ids.user_id.ids[
                            current_index] and line.skip:

                            skip = len(record.approver_line_ids.filtered(
                                lambda
                                    x: x.skip and x.user_id.id == mla_rule_obj.approver_ids.user_id.ids[
                                    current_index] and x.start_date <= fields.Datetime.now() <= x.end_date))

                            if skip:
                                line.approve_by_user_id = mla_rule_obj.approver_ids.user_id.ids[
                                    current_index]
                                line.is_approved = True
                                line.log = 'Approved by skip Procedure'
                                try:
                                    return mla_rule_obj.approver_ids.user_id.ids[current_index + 1]
                                except IndexError:
                                    return False
                            else:
                                return mla_rule_obj.approver_ids.user_id.ids[current_index]

                return mla_rule_obj.approver_ids.user_id.ids[current_index]

        return False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MultiLevelApproval, self).create(vals_list)
        mla_rule = self.env["multi.level.approval.rule"].search([('approval_model_id.model', '=', self._name)])
        for record in res:
            if mla_rule:
                for line in mla_rule.approver_ids:
                    self.env['mla.approver'].create({
                        'model': self._name,
                        'res_id': record.id,
                        'required': line.required,
                        'user_id': line.user_id.id,
                        'skip': line.skip,
                        'transfer_approvation': line.transfer_approvation,
                        'transfer_user': line.transfer_user.id,
                        'start_date': line.start_date,
                        'end_date': line.end_date,
                        'log': line.log

                    })
        return res


class MLAApprover(models.Model):
    _name = "mla.approver"
    _description = "Multilevel Approver"

    required = fields.Boolean(string='Required', index=False, store=True, readonly=False)
    user_id = fields.Many2one('res.users', string='User', index=False, store=True, readonly=False)
    is_approved = fields.Boolean("Is Approved or Not", default=False)
    approve_by_user_id = fields.Many2one('res.users', string='Approved User', index=False, store=True, readonly=False)
    model = fields.Char('Related Document Model')
    res_id = fields.Many2oneReference('Related Document ID', model_field='model')
    skip = fields.Boolean(string='Skip', index=False, store=True, readonly=False)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    log = fields.Char('Type of approval procedure')
    transfer_approvation = fields.Boolean(string='Transfer Approval', index=False, store=True, readonly=False)
    transfer_user = fields.Many2one('res.users', string='Transfer User', index=False, store=True, readonly=False)
