from odoo import models, fields, api, _

from odoo.exceptions import ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _parent_name = "parent_id"
    # _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'sequence, name'

    code = fields.Char()
    sequence = fields.Integer(string='Sequence', index=True,
                              help="Gives the sequence order when displaying "
                                   "a list of departments.")
    full_name = fields.Char('Full Name', store=True, compute='_compute_full_name')
    parent_id = fields.Many2one(ondelete='restrict')
    parent_left = fields.Integer(string='Left Parent', index=True)
    parent_right = fields.Integer(string='Right Parent', index=True)
    child_ids = fields.One2many(comodel_name='hr.department',
                                inverse_name='parent_id',
                                string='Children Departments')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code, company_id)',
         _('The code for the department must be unique per company!')),
    ]

    @api.depends('parent_id', 'name')
    def _compute_full_name(self):
        for rec in self:
            # name = rec.name if rec.name else ''
            parent_full_name = rec.parent_id.full_name if rec.parent_id else False
            rec.full_name = (parent_full_name + "/" + rec.name) if parent_full_name else rec.name


    def copy(self, default=None):
        default = dict(default or {})
        if self.name and not default.get('name'):
            # default['code'] = _("%s (copy)") % self.code
            default['name'] = _("%s (copy)") % self.name
        return super(HrDepartment, self).copy(default)

    # def name_get(self):
    #     name = self.name
    #     if self.code:
    #         name = '[%s] %s' % (self.code, name)
    #     return (self.id, name)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if name:
            search_name = name
            if operator != '=':
                search_name = '%s%%' % name
            departments = self.search([('code', operator, search_name)] + args,
                                      limit=limit)
            if departments.ids:
                return departments.name_get()
        return super(HrDepartment, self) \
            .name_search(name=name, args=args, operator=operator, limit=limit)

    @api.constrains('name')
    def _check_unique_constraint(self):
        ### Blocked by Matiar Rahman
        ### Need to consider parent department as well
        if self.name:
            filters = [['full_name', '=ilike', self.full_name]]
            name = self.search(filters)
            if len(name) > 1:
                raise ValidationError(_('[Unique Error] Department full name must be unique!'))
        return
