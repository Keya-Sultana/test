from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_ids = fields.Many2many(
        comodel_name="product.category",
        relation="product_categ_rel",
        column1="product_id",
        column2="categ_id",
        string="Extra Categories",
    )
