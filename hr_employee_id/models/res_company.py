from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    employee_id_gen_method = fields.Selection(
        selection=[
            ("random", "Random"),
            ("sequence", "Sequence"),
        ],
        string="Generation Method",
        default="random",
    )
    employee_id_random_digits = fields.Integer(
        string="# of Digits", default=5, help="Number of digits in employee identifier"
    )
    employee_id_sequence = fields.Many2one(
        comodel_name="ir.sequence",
        string="Identifier Sequence",
        help="Pattern to be used for employee identifier generation",
    )
