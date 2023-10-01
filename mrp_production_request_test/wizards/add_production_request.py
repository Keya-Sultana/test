from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AddProductionRequest(models.TransientModel):
    _name = "add.production.request"
    _description = "Wizard to Add Production request"

    production_line_ids = fields.One2many('add.production.request.line', 'production_id', string='Production Request '
                                                                                                 'Create MO',
                                          auto_join=True)

    @api.model
    def default_get(self, fields):
        res = super(AddProductionRequest, self).default_get(fields)
        manifest_data = self.env['mrp.production.request'].browse(self._context['active_id'])

        line_vals = []
        for man_item in manifest_data.order_line:
            line_vals.append([0, False, {
                'product_id': man_item.product_id.id,
                'product_uom_id': man_item.product_uom.id,
                'product_qty': man_item.product_uom_qty,
            }])

        res['production_line_ids'] = line_vals
        return res


class AddProductionRequestLine(models.TransientModel):
    _name = "add.production.request.line"
    _description = "Wizard to Add Production request line"

    production_id = fields.Many2one('add.production.request', string='Production Reference', required=True,
                                    ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=True)
    product_qty = fields.Float(string="Production Quantity", required=True, digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number',
                             domain="[('product_id', '=', product_id)]")

    #############################
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material', )
    move_raw_ids = fields.One2many('production.request.mo.line', 'request_mo_id', 'Components', copy=False, )

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    location_src_id = fields.Many2one('stock.location', 'Components Location')
    location_dest_id = fields.Many2one('stock.location', 'Finished Products Location')
    origin = fields.Char('Source')
    date_deadline = fields.Datetime('Deadline')

    move_finished_ids = fields.One2many(
        'stock.move', 'production_id', 'Finished Products',
        copy=False, domain=[('scrapped', '=', False)])
    move_byproduct_ids = fields.One2many('stock.move', compute='_compute_move_byproduct_ids',
                                         inverse='_set_move_byproduct_ids')

    ##############################
    # @api.onchange('bom_id')
    # def onchange_bom(self):
    #     if self.bom_id:
    #         bom_data = self.env['mrp.bom'].search([('id', '=', self.bom_id.id)])
    #         line_vals = []
    #         for line in bom_data.bom_line_ids:
    #             line_vals.append([0, False, {
    #                 'product_id': line.product_id.id,
    #                 "request_mo_id": self.id,
    #                 # 'product_uom_id': line.product_uom.id,
    #                 # 'product_qty': line.product_uom_qty,
    #             }])
    #         self.move_raw_ids = line_vals

    def action_show_package_details(self):
        self.ensure_one()
        view = self.env.ref('mrp_production_request_test.production_request_line_view')

        return {
            'name': _('Package Content'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'add.production.request.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'flags': {'mode': 'readonly'},
        }

    @api.depends('move_finished_ids')
    def _compute_move_byproduct_ids(self):
        for order in self:
            order.move_byproduct_ids = order.move_finished_ids.filtered(lambda m: m.product_id != order.product_id)

    def _set_move_byproduct_ids(self):
        move_finished_ids = self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id)
        self.move_finished_ids = move_finished_ids | self.move_byproduct_ids


class ProductionRequestMOLine(models.TransientModel):
    _name = "production.request.mo.line"
    _description = "Wizard to Add Production request MO line"

    request_mo_id = fields.Many2one('production.request.create.mo', string='MO Line',)
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_qty = fields.Float(string="To Consume", digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM",)
    location_id = fields.Many2one('stock.location', 'Source Location', )


