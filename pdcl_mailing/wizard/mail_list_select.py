
from odoo import api, fields, models, _
from odoo.tools.translate import _
from datetime import date, datetime


class MailList(models.Model):
    _name = "partner.list.wizard"
    _description = "Mail List"

    mail_type = fields.Selection([
        ('mailing', 'Mailings'),
        ('mail_list', 'Mailing Lists'),
        ('mail_contract', 'Mail Contract')
    ], string='Mail Type', required=True)

    mailing_id = fields.Many2one("mailing.mailing", string="Mailing", required=False)

    mail_contract_id = fields.Many2one('mailing.contact', string='Mailing Contract', required=False)
    mail_list_id = fields.Many2one('mailing.list', string='Mailing Lists', required=False)

    def make_mail(self):
        # pass
        part_obj = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        mail_obj = self.env['mailing.mailing']
        list_obj = self.env['mailing.list']
        contract_obj = self.env['mailing.contact']

        if self.mail_type == 'mailing':
            for items in part_obj:
                mail_obj.create({
                    'subject': items.name,
                    # 'mailing_model_id': items.email,
                })
        elif self.mail_type == 'mail_list':
            list_name = self.env['mailing.list'].search([('name', '=', self.mail_list_id.name)])
            print(list_name.name)

            inv_lines = []
            # for line_items in self:
            tmp = {
                'list_id': list_name.id
            }
            inv_lines.append([0, False, tmp])
            print(inv_lines)

            for items in part_obj:
                vals_list = {
                    'name': items.name,
                    'email': items.email,
                    "subscription_list_ids": inv_lines,
                }
                print(vals_list)
                contract_obj.create(vals_list)

            # for items in part_obj:
            #     contract_obj.create({
            #         'name': items.name,
            #         'email': items.email,
            #     })
            #     for line in contract_obj.subscription_list_ids:
            #         line.write({'list_id': list_name.name})
            #         print(line)
                    # values = {'list_id': list_name.name}
                    # line.write(values)
            # list_name = self.env['mailing.list'].search([('name', '=', self.mail_list_id.name)])
            # print(list_name.name)
            # for items in part_obj:
            #     contract_obj.create({
            #         'name': items.name,
            #         'email': items.email,
            #         'company_name': self.mail_list_id.name
            #     })
        elif self.mail_type == 'mail_contract':
            for items in part_obj:
                contract_obj.create({
                    'name': items.name,
                    'email': items.email,
                })

