from odoo import api, fields, models, _


class ProductionRequestCreateMO(models.TransientModel):
    """Create Manufacturing Orders by production request """
    _name = 'production.request.create.mo'
    _description = 'Production request create mo'

    product_id = fields.Many2one('product.product', 'Product', )
    product_qty = fields.Float('Quantity To Produce', default=1.0, digits='Product Unit of Measure', readonly=True, tracking=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', domain="[('category_id', '=', "
                                                                                  "product_uom_category_id)]")
    bom_id = fields.Many2one('mrp.bom', 'Bill of Material',)

    move_raw_ids = fields.One2many('production.request.mo.line', 'request_mo_id', 'Components', copy=False,)


class ProductionRequestMOLine(models.TransientModel):
    _name = "production.request.mo.line"
    _description = "Wizard to Add Production request MO line"

    request_mo_id = fields.Many2one('production.request.create.mo', string='MO Line', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=True)
    product_qty = fields.Float(string="To Consume", required=True, digits="Product Unit of Measure")
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", required=True)
    location_id = fields.Many2one('stock.location', 'Source Location',)
