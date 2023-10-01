import base64

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _name = "multi.level.approval.category"
    _description = "Multilevel Category Approval"

    def _get_default_image(self):
        default_image_path = get_module_resource('multi_level_approval', 'static/src/img', 'clipboard-check-solid.svg')
        return base64.b64encode(open(default_image_path, 'rb').read())

    active = fields.Boolean(string='Active', index=False, store=True, readonly=False, required=True
                            )
    approval_minimum = fields.Integer(string='Minimum Approval', default="1", index=False, store=True, readonly=False)
    approval_model_id = fields.Many2one('ir.model', string='Approval Model', index=False, store=True, readonly=False)
    approver_ids = fields.One2many('mla.category.approver', 'category_id', string='Approvers', index=False, store=True,
                                   readonly=False)
    company_id = fields.Many2one('res.company', string='Company', index=True, store=True, readonly=False)
    description = fields.Char(string='Description', index=False, store=True, readonly=False)
    has_amount = fields.Selection(
        CATEGORY_SELECTION,
        string='Has Amount', default="no", index=False, store=True, readonly=False)
    has_date = fields.Selection(CATEGORY_SELECTION, string='Has Date', default="no", index=False, store=True,
                                readonly=False)
    has_location = fields.Selection(CATEGORY_SELECTION, string='Has Location', default="no", index=False,
                                    store=True, readonly=False)
    has_partner = fields.Selection(CATEGORY_SELECTION, string='Has Contact', default="no", index=False,
                                   store=True, readonly=False)
    has_payment_method = fields.Selection(CATEGORY_SELECTION, string='Has Payment', default="no", index=False,
                                          store=True, readonly=False)
    has_period = fields.Selection(CATEGORY_SELECTION, string='Has Period', default="no", index=False, store=True,
                                  readonly=False)
    has_product = fields.Selection(CATEGORY_SELECTION, string='Has Product', default="no", index=False,
                                   store=True, readonly=False)
    has_quantity = fields.Selection(CATEGORY_SELECTION, string='Has Quantity', default="no", index=False,
                                    store=True, readonly=False)
    has_reference = fields.Selection(CATEGORY_SELECTION, string='Has Reference', default="no", index=False,
                                     store=True, readonly=False)
    image = fields.Binary(string='Image', index=False, store=True, readonly=False)
    invalid_minimum = fields.Boolean(string='Invalid Minimum', index=False, store=False, readonly=True,
                                     compute='_compute_invalid_minimum')
    invalid_minimum_warning = fields.Char(string='Invalid Minimum Warning', index=False, store=False, readonly=True,
                                          compute='_compute_invalid_minimum')
    manager_approval = fields.Selection([('approver', 'Is Approver'), ('required', 'Is Required Approver')],
                                        string="Employee's Manager",
                                        index=False, store=True, readonly=False, help="""How the employee's manager interacts with this type of approval.
        Empty: do nothing
        Is Approver: the employee's manager will be in the approver list
        Is Required Approver: the employee's manager will be required to approve the request.
    """)
    name = fields.Char(string='Name', index=False, store=True, readonly=False, required=True)
    request_to_validate_count = fields.Integer(string='Number of request to validate', index=False, store=False,
                                               readonly=True, compute="_compute_request_to_validate_count")
    requirer_document = fields.Selection(CATEGORY_SELECTION, string='Documents', default="no", index=False,
                                         store=True, readonly=False)


    def _compute_request_to_validate_count(self):
        domain = [('request_status', '=', 'pending'), ('approver_ids.user_id', '=', self.env.user.id)]
        requests_data = self.env['approval.request'].read_group(domain, ['category_id'], ['category_id'])
        requests_mapped_data = dict((data['category_id'][0], data['category_id_count']) for data in requests_data)
        for category in self:
            category.request_to_validate_count = requests_mapped_data.get(category.id, 0)

    @api.depends_context('lang')
    @api.depends('approval_minimum', 'approver_ids', 'manager_approval')
    def _compute_invalid_minimum(self):
        for record in self:
            if record.approval_minimum > len(record.approver_ids) + int(bool(record.manager_approval)):
                record.invalid_minimum = True
            else:
                record.invalid_minimum = False
            record.invalid_minimum_warning = record.invalid_minimum and _(
                'Your minimum approval exceeds the total of default approvers.')

    @api.constrains('approval_minimum', 'approver_ids')
    def _constrains_approval_minimum(self):
        for record in self:
            if record.approval_minimum < len(record.approver_ids.filtered('required')):
                raise ValidationError(_('Minimum Approval must be equal or superior to the sum of required Approvers.'))

    @api.constrains('approver_ids')
    def _constrains_approver_ids(self):
        # There seems to be a problem with how the database is updated which doesn't let use to an sql constraint for this
        # Issue is: records seem to be created before others are saved, meaning that if you originally have only user a
        #  change user a to user b and add a new line with user a, the second line will be created and will trigger the constraint
        #  before the first line will be updated which wouldn't trigger a ValidationError
        for record in self:
            if len(record.approver_ids) != len(record.approver_ids.user_id):
                raise ValidationError(_('An user may not be in the approver list multiple times.'))

    @api.model
    def create(self, vals):
        if len(vals['approver_ids']) == 0:
            raise ValidationError(_('You must add an approver'))
        if vals.get('automated_sequence'):
            sequence = self.env['ir.sequence'].create({
                'name': _('Sequence') + ' ' + vals['sequence_code'],
                'padding': 5,
                'prefix': vals['sequence_code'],
                'company_id': vals.get('company_id'),
            })
            vals['sequence_id'] = sequence.id

        approval_category = super().create(vals)
        return approval_category

    def write(self, vals):
        if 'sequence_code' in vals:
            for approval_category in self:
                sequence_vals = {
                    'name': _('Sequence') + ' ' + vals['sequence_code'],
                    'padding': 5,
                    'prefix': vals['sequence_code'],
                }
                if approval_category.sequence_id:
                    approval_category.sequence_id.write(sequence_vals)
                else:
                    sequence_vals['company_id'] = vals.get('company_id', approval_category.company_id.id)
                    sequence = self.env['ir.sequence'].create(sequence_vals)
                    approval_category.sequence_id = sequence
        if 'company_id' in vals:
            for approval_category in self:
                if approval_category.sequence_id:
                    approval_category.sequence_id.company_id = vals.get('company_id')
        return super().write(vals)

    def create_request(self):
        self.ensure_one()
        # If category uses sequence, set next sequence as name
        # (if not, set category name as default name).
        return {
            "type": "ir.actions.act_window",
            "res_model": "approval.request",
            "views": [[False, "form"]],
            "context": {
                'form_view_initial_mode': 'edit',
                'default_name': _('New') if self.automated_sequence else self.name,
                'default_category_id': self.id,
                'default_request_owner_id': self.env.user.id,
                'default_request_status': 'new'
            },
        }
