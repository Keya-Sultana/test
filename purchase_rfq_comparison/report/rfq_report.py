from odoo import api, exceptions, fields, models


class GbsRFQReport(models.AbstractModel):
    _name = 'report.purchase_rfq_comparison.rfq_report'
    _description = 'Gbs RFQ Report'

    @api.model
    def _get_report_values(self, docids, data):

        if docids:
            rfq_obj_pool = self.env['purchase.rfq']
            rfq_obj = rfq_obj_pool.browse(docids[0])

            vals = []
            for obj in rfq_obj.purchase_rfq_lines:
                vals.append(({'product_id': obj.product_id.name,
                              'product_qty': obj.product_qty,
                              'product_uom_id': obj.product_uom_id.name,
                              }))
            data['vals'] = vals

        return {
            'lists': data['vals'],
        }

        # return self.env['report'].render('purchase_rfq_comparison.rfq_report', docargs)