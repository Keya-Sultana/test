from odoo import _, api, fields, models
import time, datetime


class MrpProductionRequest(models.Model):
    _name = "mrp.production.request"
    _description = "Manufacturing Request"
    _inherit = "mail.thread"
    # _order = "date_planned_start desc, id desc"

    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)
    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)
    planned_date_begin = fields.Datetime("Start date", tracking=True, task_dependency_tracking=True)
    planned_date_end = fields.Datetime("End date", tracking=True, task_dependency_tracking=True)
    deadline = fields.Date(string="Deadline")
    description = fields.Text("Note")

    order_line = fields.One2many('production.request.line', 'order_id', string='Order Lines', auto_join=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string='State', readonly=True, copy=False, index=True, tracking=True, default='draft')


class ProductionRequestLine(models.Model):
    _name = 'production.request.line'
    _description = 'Production Request Line'

    order_id = fields.Many2one('mrp.production.request', string='Order Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, index=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one(
        'product.product', string='Product',
        change_default=True, ondelete='restrict', check_company=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure',
                                  domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    remark = fields.Text("Remark")

    @api.onchange('product_id')
    def onchange_product(self):
        self.product_uom = self.product_id.uom_id
