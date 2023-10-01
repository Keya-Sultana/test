from odoo import api,fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockIndentConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Stock Indent Config Settings'

    def _get_default(self):
        query = """select days_of_backdating_indent from res_config_settings order by id desc limit 1"""
        self.env.cr.execute(query)
        days_value = self.env.cr.fetchone()
        if days_value:
            return days_value[0]

    days_of_backdating_indent = fields.Integer(string='Indent Backdating', default=_get_default)

    @api.constrains('days_of_backdating_indent')
    def _check_days_of_backdating_indent(self):
        for rec in self:
            if rec.days_of_backdating_indent < 0:
                raise ValidationError(_("You can't set negative value."))

