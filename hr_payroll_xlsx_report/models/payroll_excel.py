from datetime import date, datetime
import pytz
import json
import datetime
import io
import math
from odoo.tools.misc import formatLang
from odoo import api, fields, models, _
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class HrPayrollRun(models.Model):
    _inherit = "hr.payslip.run"

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            # 'slip_ids': self.slip_ids.id,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'hr.payslip.run',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Payslip Summary Report',
                     },
            'report_type': 'xlsx'
        }

    def get_lines(self, data):
        lines = []
        rule_list = []
        no = 0
        payslip = self.browse(data['ids'])
        # print(self.browse(data['ids']).slip_ids[0].employee_id.name)
        # slip.line_ids[3]

        for slip in payslip.slip_ids:
            from_date = slip.date_from
            from_date = from_date.strftime("%m/%d/%Y")

            to_date = slip.date_to
            to_date = to_date.strftime("%m/%d/%Y")

            for line in slip.line_ids:
                if line.code == 'BASIC':
                    basic_amount = math.ceil(line.total)
                elif line.code == 'HRA':
                    hra_amount = math.ceil(line.total)
                elif line.code == 'CA':
                    ca_amount = math.ceil(line.total)
                elif line.code == 'CAGG':
                    cagg_amount = math.ceil(line.total)
                elif line.code == 'MA':
                    ma_amount = math.ceil(line.total)
                elif line.code == 'SUMALW':
                    sumalw_amount = math.ceil(line.total)
                elif line.code == 'GROSS':
                    gross_amount = math.ceil(line.total)
                elif line.code == 'PF':
                    pf_amount = math.ceil(line.total)
                elif line.code == 'PT':
                    pt_amount = math.ceil(line.total)
                else:
                    net_amount = math.ceil(line.total)

            # all_total = sum(net_amount)

            # for line in slip.line_ids:
            #     if line.appears_on_payslip is True:
            #         rule = {'name': line.name,
            #                 'seq': line.sequence,
            #                 'code': line.code}
            #
            #         if rule not in rule_list:
            #             rule_list.append(rule)
            #
            #     rule_list = sorted(rule_list, key=lambda k: k['seq'])
            #     for rule in rule_list:
            #         # payslip[rule['code']] = []
            #
            #         for line in slip.line_ids:
            #             if line.code == rule['code']:
            #                 basic_amount = math.ceil(line.total)
            #             if line.code == rule['code']:
            #                 hra_amount = math.ceil(line.total)
            #                 # payslip[rule['code']] = formatLang(self.env, total_amount)

            vals = {
                'sn': no + 1,
                'ref': slip.number,
                'employee': slip.employee_id.name,
                'job': slip.employee_id.job_id.name,
                'date_from': from_date,
                'date_to': to_date,
                'basic': basic_amount,
                'hra': hra_amount,
                'ca': ca_amount,
                'cagg': cagg_amount,
                'ma': ma_amount,
                'sumalw': sumalw_amount,
                'gross': gross_amount,
                'pf': pf_amount,
                'pt': pt_amount,
                'net': net_amount,
                # 'all_total': all_total,
            }
            lines.append(vals)
            no += 1
        return lines

    def get_xlsx_report(self, data, response):

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        lines = self.browse(data['ids'])
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz if user.tz else 'UTC')
        times = pytz.utc.localize(datetime.datetime.now()).astimezone(tz)

        # WORKSHEET
        sheet = workbook.add_worksheet('Salary Info')

        # Format
        bold = workbook.add_format({'bold': True, 'size': 10})
        name_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        address_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'size': 10})
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
        format2 = workbook.add_format({'font_size': 10, 'align': 'right', 'bold': True})
        format3 = workbook.add_format({'border': 1, 'font_size': 10, 'align': 'right', 'bold': True, 'valign': 'vcenter'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        # format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'border': 1})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right', 'border': 1})

        # SHEET HEADER
        sheet.merge_range(0, 0, 0, 9, lines.company_id.name, name_format)
        sheet.merge_range(1, 0, 1, 9, lines.company_id.street, address_format)
        sheet.merge_range(2, 0, 2, 9, lines.company_id.street2, address_format)
        sheet.merge_range(3, 0, 3, 9, lines.company_id.city + '-' + lines.company_id.zip, address_format)
        sheet.merge_range(4, 0, 4, 9, "Monthly Salary Sheet", name_format)
        sheet.merge_range(5, 0, 5, 3, "Description: " + lines.name, bold)
        sheet.merge_range(5, 7, 5, 9, 'Report Date : ' + str(times.strftime("%Y-%m-%d %H:%M %p")), format2)

        # sheet.merge_range('A8:G8', 'Report Date: ' + str(times.strftime("%Y-%m-%d %H:%M %p")), format1)

        # SET CELL HEIGHT
        sheet.set_row(9, 36)

        # SET CELL WIDTH
        sheet.set_column('A9:A9', 6)
        sheet.set_column('B9:B9', 10)
        sheet.set_column('C9:C9', 15)
        sheet.set_column('D9:D9', 20)
        sheet.set_column('E9:E9', 20)
        sheet.set_column('F9:F9', 8)
        sheet.set_column('G9:G9', 10)
        sheet.set_column('H9:H9', 10)
        sheet.set_column('I9:I9', 13)
        sheet.set_column('J9:J9', 8)
        sheet.set_column('K9:K9', 10)
        sheet.set_column('L9:L9', 8)
        sheet.set_column('M9:M9', 10)
        sheet.set_column('N9:N9', 11)
        sheet.set_column('O9:O9', 7)

        # TABLE HEADER
        sheet.merge_range(8, 0, 8 + 1, 0, 'SN', format21)
        sheet.merge_range(8, 1, 8 + 1, 1, 'Payslip Ref', format21)
        sheet.merge_range(8, 2, 8 + 1, 2, 'Employee', format21)
        sheet.merge_range(8, 3, 8 + 1, 3, 'Designation', format21)
        sheet.merge_range(8, 4, 8 + 1, 4, 'Period', format21)
        sheet.write(8, 5, 'Basic', format21)
        sheet.merge_range(8, 6, 8, 6 + 4, 'Allowance', format21)
        sheet.write(8, 11, 'Gross', format21)
        sheet.merge_range(8, 12, 8, 12 + 1, 'Deduction', format21)
        sheet.write(8, 14, 'Net', format21)
        sheet.write(9, 5, 'Basic Salary', format21)
        sheet.write(9, 6, 'House Rent Allowance', format21)
        sheet.write(9, 7, 'Conveyance Allowance', format21)
        sheet.write(9, 8, 'Conveyance Allowance For Gravie', format21)
        sheet.write(9, 9, 'Meal Voucher', format21)
        sheet.write(9, 10, 'Sum of Allowance Category', format21)
        sheet.write(9, 11, 'Gross', format21)
        sheet.write(9, 12, 'Provident Fund', format21)
        sheet.write(9, 13, 'Professional Al Tax', format21)
        sheet.write(9, 14, 'Net Salary', format21)

        # Table Body
        prod_row = 10
        prod_col = 0
        total_net = 0
        total_pf = 0
        total_pt = 0
        total_gross = 0

        get_line = self.get_lines(data)
        for each in get_line:
            sheet.write(prod_row, prod_col, each['sn'], font_size_8)
            sheet.write(prod_row, prod_col + 1, each['ref'], font_size_8)
            sheet.write(prod_row, prod_col + 2, each['employee'], font_size_8)
            sheet.write(prod_row, prod_col + 3, each['job'], font_size_8)
            sheet.write(prod_row, prod_col + 4, each['date_from'] + " To " + each['date_to'], font_size_8)
            # # sheet.merge_range(prod_row, prod_col + 8, prod_row, prod_col + 10, each['date_to'], font_size_8_r)
            sheet.write(prod_row, prod_col + 5, each['basic'], font_size_8_r)
            sheet.write(prod_row, prod_col + 6, each['hra'], font_size_8_r)
            sheet.write(prod_row, prod_col + 7, each['ca'], font_size_8_r)
            sheet.write(prod_row, prod_col + 8, each['cagg'], font_size_8_r)
            sheet.write(prod_row, prod_col + 9, each['ma'], font_size_8_r)
            sheet.write(prod_row, prod_col + 10, each['sumalw'], font_size_8_r)
            sheet.write(prod_row, prod_col + 11, each['gross'], font_size_8_r)
            sheet.write(prod_row, prod_col + 12, each['pf'], font_size_8_r)
            sheet.write(prod_row, prod_col + 13, each['pt'], font_size_8_r)
            sheet.write(prod_row, prod_col + 14, each['net'], font_size_8_r)
            prod_row = prod_row + 1
            # break
            # All column summation
            total_gross = total_gross + each['gross']
            total_pf = total_pf + each['pf']
            total_pt = total_pt + each['pt']
            total_net = total_net + each['net']

        sheet.merge_range(prod_row + 1, prod_col + 12, prod_row + 1, prod_col + 14, 'Total Net Salary : ' + str(total_net), format3)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
