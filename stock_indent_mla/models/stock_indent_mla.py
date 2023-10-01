
import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
class SalesOrder(models.Model):
    _name = "indent.indent"
    _inherit = ["indent.indent", "multi.level.approval"]


class IndentProductLines(models.Model):
    _inherit = 'indent.product.lines'

    current_user_is_approver_or_not = fields.Boolean(string='Current user is approver',
                                                     related='indent_id.current_user_is_approver_or_not')


