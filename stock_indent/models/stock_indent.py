import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class IndentIndent(models.Model):
    _name = 'indent.indent'
    _description = "Indent"
    _inherit = ['mail.thread']
    _order = "approve_date desc"

    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env.company.id
        warehouse_ids = warehouse_obj.sudo().search(
            [('company_id', '=', company_id)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    @api.model
    def _get_required_date(self):
        return datetime.strftime(datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _get_indent_type(self):
        first_indent_type = self.env['indent.type'].search([], limit=1)
        return first_indent_type and first_indent_type[0] or False

    name = fields.Char('Indent #', size=30, readonly=True,
                       default="/", copy=False)
    approve_date = fields.Datetime(
        'Approve Date', readonly=True, tracking=True)
    indent_date = fields.Datetime('Indent Date', required=True, readonly=True,
                                  default=fields.Datetime.now)
    required_date = fields.Date('Required Date', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                default=lambda self: self._get_required_date())
    indentor_id = fields.Many2one('res.users', string='Indentor', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user)
    stock_location_id = fields.Many2one('stock.location', string='Location', readonly=True, required=True,
                                        states={
                                            'draft': [('readonly', False)]},
                                        help="Default User Location.Which consider as Destination location.",
                                        default=lambda self: self.env.user.default_location_id)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]})
    requirement = fields.Selection([('0', 'Ordinary'), ('1', 'Urgent')], 'Priority', readonly=True,
                                   default="0", required=True, states={'draft': [('readonly', False)]})
    indent_type = fields.Many2one('indent.type', string='Type', readonly=True,
                                  default=lambda self: self._get_indent_type(),
                                  states={'draft': [('readonly', False)]})
    product_lines = fields.One2many('indent.product.lines', 'indent_id', 'Products Line', readonly=True,
                                    states={'draft': [('readonly', False)], 'waiting_approval': [('readonly', False)]},
                                    tracking=True)
    picking_id = fields.Many2one('stock.picking', 'Picking', copy=False)
    in_picking_id = fields.Many2one('stock.picking', 'In Picking')
    description = fields.Text('Additional Information', readonly=True, states={
        'draft': [('readonly', False)]})
    material_required_for = fields.Text('Required For', readonly=True, states={
        'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.company, required=True)
    active = fields.Boolean('Active', default=True)
    approver_id = fields.Many2one('res.users', string='Approve Authority', readonly=True,
                                  help="who have approve or reject indent.", tracking=True)
    closer_id = fields.Many2one('res.users', string='Close Authority', readonly=True, help="who have close indent.",
                                tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True, required=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="Default Warehouse.Source location.",
                                   states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type',
                                      compute='_compute_default_picking_type', readonly=True, store=True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method',
                                 readonly=True, required=True, default='direct',
                                 states={'draft': [('readonly', False)], 'cancel': [
                                     ('readonly', True)]},
                                 help="It specifies goods to be deliver partially or all at once")

    pr_indent_check = fields.Boolean(string='Indent List Check', default=True)
    is_inventory_user = fields.Boolean(
        string="check field", compute='get_user')

    days_of_backdating_indent = fields.Integer(string='Backdating Indent')

    product_id = fields.Many2one(
        'product.product', 'Products',
        readonly="1", related='product_lines.product_id',
        help="This comes from the product form.")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('received', 'Issued'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, tracking=True, default='draft')

    # _sql_constraints = [
    #     ('name_uniq', 'unique(name)', 'This Indent N0. is already in use')
    # ]

    ####################################################
    # Business methods
    ####################################################
    # @api.multi
    @api.depends('indentor_id')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('stock.group_stock_user'):
            self.is_inventory_user = True
        else:
            self.is_inventory_user = False

    # @api.onchange('indentor_id')
    # def onchange_indentor_id(self):
    #     if self.indentor_id:
    #         self.stock_location_id = self.indentor_id.default_location_id
    # else:
    #     res_date = datetime.date.today().strftime('%Y-%m-%d')

    @api.depends('product_lines.product_id')
    def _compute_days_of_backdating(self):
        for rec in self:
            for line in rec.product_lines:
                if line.product_id.categ_id.is_backdateable:
                    query = """select days_of_backdating_indent from stock_indent_config_settings order by id desc limit 1"""
                    self.env.cr.execute(query)
                    days_value = self.env.cr.fetchone()
                    if days_value:
                        rec.days_of_backdating_indent = days_value[0]
                        break
                    else:
                        rec.days_of_backdating_indent = 0
                        break
                else:
                    rec.days_of_backdating_indent = 0

    @api.constrains('indent_date')
    def _check_indent_date(self):
        days_delay = datetime.strftime((datetime.today() - timedelta(days=self.days_of_backdating_indent)).date(),
                                       DEFAULT_SERVER_DATETIME_FORMAT)
        indent_date = datetime.strftime(self.indent_date, "%Y-%m-%d %H:%M:%S")
        if indent_date < days_delay:
            raise ValidationError(
                _("As per Indent configuration back date entry can't be less then %s days.") % self.days_of_backdating_indent)

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            return {'domain': {
                'stock_location_id': [('id', 'in', self.env.user.location_ids.ids), ('can_request', '=', True)]}}

    @api.constrains('required_date')
    def _check_required_date(self):
        required_date = str(str(self.required_date) + ' 23:59:59')
        indent_date = datetime.strftime(self.indent_date, "%Y-%m-%d %H:%M:%S")
        if required_date <= indent_date:
            raise UserError(
                'Required Date can not be less then current date!!!')

    @api.depends('warehouse_id', 'stock_location_id')
    def _compute_default_picking_type(self):
        for indent in self:
            picking_type_obj = indent.env['stock.picking.type']

            # Find picking type based on indivitual location
            picking_type_ids = picking_type_obj.sudo().search(
                [('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),
                 ('default_location_dest_id', '=', indent.stock_location_id.id)])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False

            # Find picking type based on default location
            if not picking_type_id:
                picking_type_ids = picking_type_obj.sudo().search(
                    [('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),
                     ('code', '=', 'internal')])
                picking_type_id = picking_type_ids and picking_type_ids[0] or False

            indent.picking_type_id = picking_type_id

    @api.constrains('picking_type_id')
    def _check_picking_type(self):
        if not self.picking_type_id:
            raise ValidationError(_('No Picking Type For this Department.'
                                    'Please Create a picking type or contact with system Admin.'))

    @api.onchange('requirement')
    def onchange_requirement(self):
        days_delay = 0
        if self.requirement == '2':
            days_delay = 0
        if self.requirement == '1':
            days_delay = 7
        required_day = datetime.strftime(datetime.today() + timedelta(days=days_delay),
                                         DEFAULT_SERVER_DATETIME_FORMAT)
        self.required_date = required_day

    def approve_indent(self):
        res = {
            'state': 'inprogress',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.product_lines.write({'state': 'inprogress'})
        self.write(res)

    def reject_indent(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.product_lines.write({'state': 'reject'})
        self.write(res)

    def action_close_indent(self):
        res = {
            'state': 'received',
            'closer_id': self.env.user.id,
        }
        self.product_lines.write({'state': 'received'})
        self.write(res)

    def indent_confirm(self):
        for indent in self:
            if not indent.product_lines:
                raise UserError(
                    _('Unable to confirm an indent without product. Please add product(s).'))
            if indent.product_lines:
                for line in indent.product_lines:
                    if line.product_uom_qty <= 0:
                        raise UserError(
                            _('Unable to confirm an indent without product quantity.'))

            # Add all authorities of the indent as followers
            # followers = []
            # if indent.indentor_id and indent.indentor_id.partner_id and indent.indentor_id.partner_id.id:
            #     followers.append(indent.indentor_id.partner_id.id)
            # if indent.indentor_id.employee_ids[0].parent_id:
            #     followers.append(indent.indentor_id.employee_ids[0].parent_id.user_id.partner_id.id)
            # if indent.manager_id and indent.manager_id.partner_id and indent.manager_id.partner_id.id:
            #    followers.append(indent.manager_id.partner_id.id)
            # for follower in followers:
            #    indent.write({'message_follower_ids': [(4, follower)]})

            res = {
                'state': 'waiting_approval'
            }
            requested_date = self.required_date
            new_seq = self.env['ir.sequence'].sudo().next_by_code(
                'indent.indent', requested_date)
            if new_seq:
                res['name'] = new_seq

            indent.write(res)
            indent.product_lines.write({'state': 'waiting_approval'})

    def action_picking_create(self, products):
        picking_id = False
        if products:
            picking_id = self.create_picking_and_moves(products)
        self.write({'picking_id': picking_id})
        return picking_id

    def create_picking_and_moves(self, products):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in products:
            date_planned = datetime.strptime(
                str(self.indent_date), DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    pick_name = self.env['stock.picking.type'].browse(
                        self.picking_type_id.id).sequence_id.next_by_id()
                    location_id = self.warehouse_id.sudo().lot_stock_id.id
                    vals = {
                        # 'invoice_state': 'none',
                        'picking_type_id': self.picking_type_id.id,
                        'priority': self.requirement,
                        'name': pick_name,
                        'origin': self.name,
                        'date': self.indent_date,
                        'state': 'draft',
                        'move_type': self.move_type,
                        'partner_id': self.indentor_id.partner_id.id or False,
                        'location_id': location_id,
                        'location_dest_id': self.stock_location_id.id,
                        'company_id': self.company_id.id
                    }

                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id

                moves = {
                    'name': line.name,
                    'indent_id': self.id,
                    'picking_id': picking_id,
                    'picking_type_id': self.picking_type_id.id or False,
                    'product_id': line.product_id.id,
                    'date': date_planned,
                    # 'date_expected': date_planned,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': location_id,
                    'location_dest_id': self.stock_location_id.id,
                    'origin': self.name,
                    'state': 'draft',
                    'price_unit': line.product_id.standard_price or 0.0,
                    'company_id': self.company_id.id
                }

                move_obj.create(moves)
        return picking_id

    def _get_picking_id(self):
        picking_id = self.picking_id.id
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(picking_id)
        if picking.state != 'done':
            return [picking.id]
        elif picking.state == 'done' and self.state == 'inprogress':
            picking_ids = picking_obj.search([('origin', '=', self.name)])
            return picking_ids.ids
        return False

    def action_view_picking(self):
        # products = self.product_lines.filtered(lambda x: x.qty_available_now > 0)
        products = self.product_lines
        if not products:
            raise UserError('Stock not available for any products!!!')
        for product in products:
            # if product.qty_available_now <= 0:
            #     raise UserError('Stock not available!!!')
            if product.qty_available_now < product.product_uom_qty:
                product.issue_qty = product.qty_available_now
            else:
                product.issue_qty = product.product_uom_qty
        if self.picking_id:
            pass
        else:
            self.action_picking_create(products)
            self.picking_id.action_confirm()
            self.picking_id.action_assign()

        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_ids = self._get_picking_id()

        for p in self.env['stock.picking'].browse(pick_ids):
            if p.state == 'confirmed':
                p.action_assign()

        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + \
                               ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    def action_get_stock_picking(self):
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [
            '|', ('id', '=', self.picking_id.id), ('origin', '=', self.name)]
        return action

    def action_print(self):
        data = {}
        # data['picking_id'] = self.id
        return self.env.ref('stock_indent.action_report_indent_indent').report_action(None, data=data)
        # return self.env["report"].get_action(self, 'stock_indent.report_stock_indent_view', data)

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        if users_obj.has_group('stock_indent.group_stock_indent_approver'):
            domain = [
                ('state', 'in', ['waiting_approval'])]
            return domain
        elif users_obj.has_group('stock.group_stock_user'):
            domain = [
                ('state', 'in', ['inprogress'])]
            return domain
        else:
            return False

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this indent'))

        return super(IndentIndent, self).unlink()

    # def _get_all_indent_count(self):
    #     # counts of all indents grouped by indent types
    #     query = """
    #         SELECT 
    #             indt.id, 
    #             indt.name AS indent_type, 
    #             COUNT(ind.id) AS indent_type_count
    #         FROM
    #             indent_type indt
    #         LEFT JOIN 
    #             indent_indent ind
    #         ON
    #             indt.id = ind.indent_type
    #         WHERE
    #             (ind.company_id = %s OR ind.company_id IS NULL)
    #         GROUP BY
    #             indt.id
    #         ORDER BY
    #             indt.id ASC;
    #     """

    #     self.env.cr.execute(query, (self.env.company.id,))
    #     result = self.env.cr.dictfetchall()

    #     return result

    # def _get_my_indent_count(self):
    #     # counts of all indents grouped by indent types
    #     query = """
    #         SELECT 
    #             indt.id, 
    #             indt.name AS indent_type, 
    #             COUNT(ind.id) AS indent_type_count
    #         FROM
    #             indent_type indt
    #         LEFT JOIN 
    #             indent_indent ind
    #         ON
    #             indt.id = ind.indent_type
    #         WHERE
    #             (ind.company_id = %s OR ind.company_id IS NULL)
    #         AND
    #             (ind.indentor_id = %s OR ind.indentor_id IS NULL)
    #         GROUP BY
    #             indt.id
    #         ORDER BY
    #             indt.id ASC;
    #     """

    #     self.env.cr.execute(query, (self.env.company.id, self.env.uid))
    #     result = self.env.cr.dictfetchall()

    #     return result

    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the indent views.
        """
        self.check_access_rights('read')

        result = {
            'all_to_send': 0,
            'all_waiting': 0,
            'all_issued': 0,
            'my_to_send': 0,
            'my_waiting': 0,
            'my_issued': 0,
            'all_indent_types': [],
            'my_indent_types': [],
            'total_indent_type': 0,
            'total_indents': 0,
            'my_total_indents': 0,
        }

        # counts grouped by state
        indent = self.env['indent.indent']
        result['all_to_send'] = indent.search_count(
            [('state', '=', 'inprogress'), ('company_id', '=', self.env.company.id)])
        result['my_to_send'] = indent.search_count(
            [('state', '=', 'inprogress'), ('indentor_id', '=', self.env.uid),
                    ('company_id', '=', self.env.company.id)])
        result['all_waiting'] = indent.search_count(
            [('state', '=', 'waiting_approval'), ('company_id', '=', self.env.company.id)])
        result['my_waiting'] = indent.search_count(
            [('state', '=', 'waiting_approval'), ('indentor_id', '=', self.env.uid),
                    ('company_id', '=', self.env.company.id)])
        result['all_issued'] = indent.search_count(
            [('state', '=', 'received'), ('company_id', '=', self.env.company.id)])
        result['my_issued'] = indent.search_count(
            [('state', '=', 'received'), ('indentor_id', '=', self.env.uid),
                    ('company_id', '=', self.env.company.id)])
        result['total_indents'] = indent.search_count([('company_id', '=', self.env.company.id)])
        result['my_total_indents'] = indent.search_count([('indentor_id', '=', self.env.uid),
                    ('company_id', '=', self.env.company.id)])

        # counts grouped by indent_type
        # result['all_indent_types'] = self._get_all_indent_count()
        # result['my_indent_types'] = self._get_my_indent_count()
        result['all_indent_types'] = indent.read_group([('company_id', '=', self.env.company.id)],
                                                       fields=['indent_type'], groupby=['indent_type'], orderby='id')
        result['my_indent_types'] = indent.read_group(
            [('indentor_id', '=', self.env.uid), ('company_id', '=', self.env.company.id)],
            ['indent_type'], groupby=['indent_type'], orderby='id')
        result['total_indent_type'] = len(result['all_indent_types'])

        return result


class IndentProductLines(models.Model):
    _name = 'indent.product.lines'
    _description = 'Indent Product Lines'

    indent_id = fields.Many2one(
        'indent.indent', string='Indent', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, tracking=True)
    requested_qty = fields.Float(
        'Initial Demand', digits='Product UoS', tracking=True)
    product_uom_qty = fields.Float(
        'Approved Qty', digits='Product UoS', tracking=True, )
    received_qty = fields.Float('Received Qty', digits='Product UoS', help="Receive Quantity which Update by done quntity.",
                                tracking=True)
    issue_qty = fields.Float('Issued Qty', digits='Product UoS',
                             help="Issued Quantity which Update by avilable quantity.", tracking=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True,
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id')
    price_unit = fields.Float(related='product_id.standard_price', string='Price', digits='Product Price', store=True,
                              help="Price computed based on the last purchase order approved.", tracking=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount_subtotal', digits='Account',
                                  store=True)
    qty_available = fields.Float(string='On Hand', compute='_compute_product_qty', compute_sudo=True,
                                 help="Quantity on hand when indent issued")
    qty_available_now = fields.Float(string='In Stock Now', compute='_compute_product_qty', compute_sudo=True,
                                     help="Always updated Quantity")
    name = fields.Char(related='product_id.name',
                       string='Specification', store=True, tracking=True)
    remarks = fields.Text('Remarks', tracking=True)
    sequence = fields.Integer('Sequence')
    is_indent_approve = fields.Boolean(
        string="Is Indent Approve?", compute='get_indent_approve')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('received', 'Issued'),
        ('reject', 'Rejected'),
    ], string='State', default='draft')

    ####################################################
    # Business methods
    ####################################################
    # @api.depends('indentor_id')
    def get_indent_approve(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if not res_user.has_group('stock_indent.group_stock_indent_approver'):
            self.is_indent_approve = False
        else:
            self.is_indent_approve = True

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        # GET DEFAULT PRODUCT UOM
        if not (self.product_uom and self.product_id.uom_id.category_id == self.product_uom_category_id):
            self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id

    @api.constrains('product_id')
    def check_product_id(self):
        for rec in self:
            duplicate_products = rec.indent_id.product_lines.filtered(
                lambda r: r.product_id.id == rec.product_id.id)
            if len(duplicate_products) > 1:
                raise ValidationError('You can not select same product')

    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        for line in self:
            if line.product_uom_qty < 0:
                raise UserError('You can\'t give negative value!!!')

    @api.onchange('requested_qty')
    def onchange_product_uom_qty(self):
        if self.requested_qty:
            self.product_uom_qty = float(self.requested_qty)
        else:
            self.product_uom_qty = 0.00

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount_subtotal(self):
        for line in self:
            line.price_subtotal = (line.product_uom_qty * line.price_unit)

    @api.depends('product_id')
    def _compute_product_qty(self):
        for product in self:
            location_id = product.indent_id.warehouse_id.sudo().lot_stock_id.id
            product_quant = self.env['stock.quant'].search([('product_id', '=', product.product_id.id),
                                                            ('location_id', '=', location_id)])
            quantity = sum([val.quantity for val in product_quant])
            product.qty_available = quantity
            product.qty_available_now = quantity

    def _valid_field_parameter(self, field, name):
        # EXTENDS models
        return name == 'tracking' or super()._valid_field_parameter(field, name)
