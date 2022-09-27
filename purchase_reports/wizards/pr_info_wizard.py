from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PurchaseRequisitionInfoWizard(models.TransientModel):
    _name = 'purchase.requisition.info.wizard'

    pr_no = fields.Char(string='Purchase Req. No.')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    type = fields.Selection([('all', 'All'), ('local', 'Local'), ('foreign', 'Foreign')],
                            default='all', string='Type')
    operating_unit_ids = fields.Many2many('operating.unit', string='Operating Unit',
                                          domain=lambda self: [("company_id", "=", self.env.user.company_id.id)],
                                          default=lambda self: self.env.user.default_operating_unit_id)
    is_only_pending = fields.Boolean(string='Only Pending')

    @api.constrains('date_from', 'date_to', 'pr_no')
    def _check_date_validation(self):
        if not self.pr_no and not self.date_from and not self.date_to:
            raise ValidationError(_("Give Requisition No. or Between Date."))

        elif self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(_("From date must be less then To date."))
            elif (datetime.strptime(self.date_to, '%Y-%m-%d') - datetime.strptime(self.date_from, '%Y-%m-%d')).days > 90:
                raise ValidationError(_("Maximum date range are three months."))

        elif self.date_from and not self.date_to:
            raise ValidationError(_("Fill To date."))

        elif not self.date_from and self.date_to:
            raise ValidationError(_("Fill From date."))

    @api.multi
    def get_operating_unit_name(self):
        name = ''
        for rec in self.operating_unit_ids:
            name += rec.name + ', '
        return name[:-2]

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='purchase_reports.pr_info_xlsx')

    @api.multi
    def button_print_pdf(self):
        data = dict()
        data['pr_no'] = self.pr_no
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        data['type'] = self.type
        data['operating_unit_ids'] = tuple(self.operating_unit_ids.ids)
        data['operating_unit_name'] = self.get_operating_unit_name()
        data['is_only_pending'] = self.is_only_pending

        return self.env['report'].get_action(self, 'purchase_reports.report_pr_info', data=data)