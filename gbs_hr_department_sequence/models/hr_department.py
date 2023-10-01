from odoo import models, fields, api, _


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
    # parent_id = fields.Many2one(ondelete='restrict')
    # parent_left = fields.Integer(string='Left Parent', index=True)
    # parent_right = fields.Integer(string='Right Parent', index=True)
    # child_ids = fields.One2many(comodel_name='hr.department',
    #                             inverse_name='parent_id',
    #                             string='Children Departments')
    # active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code, company_id)',
         _('The code for the department must be unique per company!')),
    ]

    def copy(self, default=None):
        default = dict(default or {})
        if self.code and not default.get('code'):
            default['code'] = _("%s (copy)") % self.code
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
        return super(HrDepartment, self)\
            .name_search(name=name, args=args, operator=operator, limit=limit)

    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')