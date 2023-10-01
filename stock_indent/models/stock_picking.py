from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.update_indent_issue_qty()

        return res

    def update_indent_issue_qty(self):
        for picking in self:
            if picking.state == 'done':
                for indent in self.env['indent.indent'].search([('name', '=', picking.origin)]):
                    issue_flag = True
                    for product_line in indent.product_lines:
                        move = picking.move_line_ids.filtered(lambda o: o.product_id == product_line.product_id)
                        if picking.backorder_id:
                            product_line.write({'issue_qty': product_line.issue_qty + move.qty_done})
                        else:
                            product_line.write({'issue_qty': move.qty_done})

                        if product_line.issue_qty < product_line.product_uom_qty:
                            issue_flag = False

                    if issue_flag:
                        indent.write({'state': "received"})

        return True
