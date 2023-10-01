# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import csv
import base64
import xlrd
from odoo.tools import ustr
import requests
import codecs

import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class import_leave_wizard(models.TransientModel):
    _name = "import.leave.wizard"
    _description = "Import Leave Wizard"

    import_type = fields.Selection([('csv', 'CSV File'),
                                    ('excel', 'Excel File')],
                                   default="csv",
                                   string="Import File Type",
                                   required=True)
    file = fields.Binary(string="File", required=True)

    method = fields.Selection([('create', 'Create Leave'),
                               ('write', 'Create or Update Leave')],
                              default="create",
                              string="Method",
                              required=True)

    # product_update_by = fields.Selection([
    #     ('name', 'Name'),
    #     ('barcode', 'Barcode'),
    #     ('int_ref', 'Internal Reference'),
    # ],
    #                                      default='name',
    #                                      string="Product Variant Update By",
    #                                      required=True)

    # is_create_m2m_record = fields.Boolean(
    #     string="Create a New Record for Dynamic M2M Field (if not exist)?")

    # is_create_categ_id_record = fields.Boolean(
    #     string="Create a New Record for Product Category Field (if not exist)?"
    # )
    is_create_time_off_type_id_record = fields.Boolean(
        string="Create a New Record for Time Off Type Field (if not exist)?"
    )

    def create_internal_category(self, categ_complete_name):
        categs_ids_list = []
        previous_categ = False
        for x in categ_complete_name.split('/'):
            x = x.strip()
            if x != '':
                search_categ = self.env['product.category'].sudo().search(
                    [('name', '=', x)], limit=1)
                if search_categ:
                    categs_ids_list.append(search_categ.id)
                    if previous_categ:
                        search_categ.update({'parent_id': previous_categ})
                    previous_categ = search_categ.id
                else:
                    # create new one
                    if previous_categ:
                        categ_id = self.env['product.category'].sudo().create({
                            'name':
                                x,
                            'parent_id':
                                previous_categ
                        })
                    else:
                        categ_id = self.env['product.category'].sudo().create(
                            {'name': x})
                    categs_ids_list.append(categ_id.id)

                    previous_categ = categ_id.id

    # ====================================================================================
    # Validation methods for custom field
    # ====================================================================================

    def validate_field_value(self, field_name, field_ttype, field_value,
                             field_required, field_name_m2o):
        """ Validate field value, depending on field type and given value """
        self.ensure_one()

        try:
            checker = getattr(self, 'validate_field_' + field_ttype)
        except AttributeError:
            _logger.warning(field_ttype +
                            ": This type of field has no validation method")
            return {}
        else:
            return checker(field_name, field_ttype, field_value,
                           field_required, field_name_m2o)

    def validate_field_many2many(self, field_name, field_ttype, field_value,
                                 field_required, field_name_m2o):
        self.ensure_one()

        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            name_relational_model = self.env['product.product'].fields_get(
            )[field_name]['relation']

            ids_list = []
            if field_value.strip() not in (None, ""):
                for x in field_value.split(','):
                    x = x.strip()
                    if x != '':
                        record = self.env[name_relational_model].sudo().search(
                            [(field_name_m2o, '=', x)], limit=1)

                        # ---------------------------------------------------------
                        # if m2m record not found then create a new record for it.
                        # if tick in wizard.

                        # if self.is_create_m2m_record and not record:
                        #     try:
                        #         record = self.env[name_relational_model].sudo(
                        #         ).create({field_name_m2o: x})
                        #     except Exception as e:
                        #         msg = " - Value is not valid. " + ustr(e)
                        #         return {"error": " - " + x + msg}
                        #         break
                        # ---------------------------------------------------------
                        # if m2m record not found then create a new record for it.

                        if record:
                            ids_list.append(record.id)
                        else:
                            return {"error": " - " + x + " not found. "}
                            break

            return {field_name: [(6, 0, ids_list)]}

    def validate_field_many2one(self, field_name, field_ttype, field_value,
                                field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            name_relational_model = self.env['product.product'].fields_get(
            )[field_name]['relation']
            record = self.env[name_relational_model].sudo().search(
                [(field_name_m2o, '=', field_value)], limit=1)
            return {field_name: record.id if record else False}

    def validate_field_text(self, field_name, field_ttype, field_value,
                            field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_integer(self, field_name, field_ttype, field_value,
                               field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_float(self, field_name, field_ttype, field_value,
                             field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_char(self, field_name, field_ttype, field_value,
                            field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}
        else:
            return {field_name: field_value or False}

    def validate_field_boolean(self, field_name, field_ttype, field_value,
                               field_required, field_name_m2o):
        self.ensure_one()
        #         if field_required and field_value in (None,""):
        #             return {"error" : " - " + field_name + " is required. "}
        #         else:
        boolean_field_value = False
        if field_value.strip() == 'TRUE':
            boolean_field_value = True

        return {field_name: boolean_field_value}

    def validate_field_selection(self, field_name, field_ttype, field_value,
                                 field_required, field_name_m2o):
        self.ensure_one()
        if field_required and field_value in (None, ""):
            return {"error": " - " + field_name + " is required. "}

        # get selection field key and value.
        selection_key_value_list = self.env['product.product'].sudo(
        )._fields[field_name].selection
        if not isinstance(selection_key_value_list, list):
            selection_key_value_list = self.env['product.template'].sudo(
            )._fields[field_name].selection

        if selection_key_value_list and field_value not in (None, ""):
            for tuple_item in selection_key_value_list:
                if tuple_item[1] == field_value:
                    return {field_name: tuple_item[0] or False}

            return {
                "error":
                    " - " + field_name + " given value " + str(field_value) +
                    " does not match for selection. "
            }

        # finaly return false
        if field_value in (None, ""):
            return {field_name: False}

        return {field_name: field_value or False}

    # ====================================================================================
    # Validation methods for custom field
    # ====================================================================================

    def show_success_msg(self, counter, skipped_line_no):

        # open the new success message box
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k, v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context,
        }

    def read_xls_book(self):
        book = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        values_sheet = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value) if is_float else str(int(cell.value)))
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(
                        cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT
                                    ) if is_datetime else dt.
                            strftime(DEFAULT_SERVER_DATE_FORMAT))
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s"
                          ) % {
                            'row':
                                rowx,
                            'col':
                                colx,
                            'cell_value':
                                xlrd.error_text_from_code.get(
                                    cell.value,
                                    _("unknown error code %s") % cell.value)
                        })
                else:
                    values.append(cell.value)
            values_sheet.append(values)
        return values_sheet

    def import_leave_apply(self):

        leave_obj = self.env['hr.leave']
        ir_model_fields_obj = self.env['ir.model.fields']

        # perform import lead
        if self and self.file:
            skip_header = True

            # For CSV
            if self.import_type == 'csv' or self.import_type == 'excel':
                counter = 1
                skipped_line_no = {}
                row_field_dic = {}
                row_field_error_dic = {}

                try:
                    values = []
                    if self.import_type == 'csv':
                        file = str(
                            base64.decodebytes(self.file).decode('utf-8'))
                        values = csv.reader(file.splitlines())

                    elif self.import_type == 'excel':
                        values = self.read_xls_book()

                    for row in values:
                        try:
                            if skip_header:
                                skip_header = False
                                continue

                            _logger.info("Start processing row number " + str(counter))
                            _logger.info(row)
                            tmpl_vals = {}
                            if row[0].strip() in (None, ""):
                                skipped_line_no[str(
                                    counter
                                )] = " - Employee  not found. "
                                counter = counter + 1
                                continue
                            else:
                                search_emp = self.env['hr.employee'].search([('name', '=', row[0])],
                                                                            limit=1)
                                if not search_emp:
                                    skipped_line_no[str(
                                        counter
                                    )] = " - Employee  not found. "
                                    counter = counter + 1
                                    continue

                            tmpl_vals.update({'employee_id': search_emp.id})

                            if row[1].strip() in (None, ""):
                                skipped_line_no[str(
                                    counter
                                )] = " - Time Off type  not found. "
                                counter = counter + 1
                                continue
                            else:
                                search_time_off_type = self.env['hr.leave.type'].search(
                                    [('name', '=', row[1].strip())],
                                    limit=1)
                                if not search_time_off_type:
                                    skipped_line_no[str(
                                        counter
                                    )] = " - Time Off type  not found. "
                                    counter = counter + 1
                                    continue

                            tmpl_vals.update({'holiday_status_id': search_time_off_type.id})

                            if row[2].strip() in (None, ""):
                                skipped_line_no[str(
                                    counter
                                )] = " - Start date  not found. "
                                counter = counter + 1
                                continue
                            else:
                                tmpl_vals.update({'request_date_from': row[2].strip()})
                                tmpl_vals.update({'date_from': row[2].strip()})

                            if row[3].strip() in (None, ""):
                                skipped_line_no[str(
                                    counter
                                )] = " - Start date  not found. "
                                counter = counter + 1
                                continue
                            else:
                                tmpl_vals.update({'request_date_to': row[3].strip()})
                                tmpl_vals.update({'date_to': row[3].strip()})

                            if row[4].strip() in (None, ""):
                                num_of_days = 0.0
                            else:
                                num_of_days = float(row[4].strip()[2:])
                            tmpl_vals.update({'number_of_days': num_of_days})

                            is_refused = False
                            is_confirmed = False
                            is_validate = False
                            is_validate1 = False

                            leave_status = row[5].strip()
                            if leave_status not in (None, ""):
                                tmpl_vals.update({'state': 'draft'})
                                if leave_status == 'To Submit':
                                    tmpl_vals.update({'state': 'draft'})
                                elif leave_status == 'To Approve':
                                    is_confirmed = True
                                    # tmpl_vals.update({'state': 'confirm'})
                                elif leave_status == 'Approved':
                                    is_validate = True
                                    # tmpl_vals.update({'state': 'confirm'})
                                elif leave_status == 'Second Approval':
                                    is_validate1 = True
                                    # tmpl_vals.update({'state': 'confirm'})
                                elif leave_status == 'Refused':
                                    is_refused = True
                                    # tmpl_vals.update({'state': 'refuse'})

                            leave_year = self.env['date.range'].search([('name', '=', row[6].strip())])
                            tmpl_vals.update({'leave_year_id': leave_year.id})

                            # tmpl_vals.update({'sale_ok': True})
                            # if row[2].strip() == 'FALSE':
                            #     tmpl_vals.update({'sale_ok': False})
                            #
                            # tmpl_vals.update({'purchase_ok': True})
                            # if row[3].strip() == 'FALSE':
                            #     tmpl_vals.update(
                            #         {'purchase_ok': False})
                            #
                            # if row[4].strip() == 'Service':
                            #     tmpl_vals.update({'type': 'service'})
                            # elif row[4].strip() == 'Storable Product':
                            #     tmpl_vals.update({'type': 'product'})
                            # elif row[4].strip() == 'Consumable':
                            #     tmpl_vals.update({'type': 'consu'})
                            #
                            # if row[5].strip() in (None, ""):
                            #     search_category = self.env[
                            #         'product.category'].search([
                            #         ('complete_name', '=', 'All')
                            #     ],
                            #         limit=1)
                            #     if search_category:
                            #         tmpl_vals.update({
                            #             'categ_id':
                            #                 search_category.id
                            #         })
                            #     else:
                            #         skipped_line_no[str(
                            #             counter
                            #         )] = " - Category - All  not found. "
                            #         counter = counter + 1
                            #         continue
                            # else:
                            #     search_category = self.env[
                            #         'product.category'].search(
                            #         [('complete_name', '=',
                            #           row[5].strip())],
                            #         limit=1)

                            # -----------------------------------------
                            # if category not found then create new
                            # client specific.
                            # if not search_category:
                            #     if self.is_create_time_off_type_id_record:
                            #         self.create_internal_category(
                            #             row[5].strip())
                            #
                            #         search_category = self.env[
                            #             'product.category'].search(
                            #                 [('complete_name', '=',
                            #                   row[5].strip())],
                            #                 limit=1)

                            # -----------------------------------------
                            # if category not found then create new

                            # if search_category:
                            #     tmpl_vals.update({
                            #         'categ_id':
                            #             search_category.id
                            #     })
                            # else:
                            #     skipped_line_no[str(
                            #         counter
                            #     )] = " - Category - %s not found. " % (
                            #         row[5].strip())
                            #     counter = counter + 1
                            #     continue
                            #                                     if row[5].strip() in (None,""):
                            #                                         search_category = self.env['product.category'].search([('complete_name','=','All')], limit = 1)
                            #                                         if search_category:
                            #                                             tmpl_vals.update({'categ_id' : search_category.id })
                            #                                         else:
                            #                                             skipped_line_no[str(counter)] = " - Category -  not found. "
                            #                                             counter = counter + 1
                            #                                             continue
                            #                                     else:
                            #                                         search_category = self.env['product.category'].search([('complete_name','=',row[5].strip())], limit = 1)
                            #                                         if search_category:
                            #                                             tmpl_vals.update({'categ_id' : search_category.id })
                            #                                         else:
                            #                                             skipped_line_no[str(counter)] = " - Category not found. "
                            #                                             counter = counter + 1
                            #                                             continue

                            # if row[6].strip() in (None, ""):
                            #     search_uom = self.env[
                            #         'uom.uom'].search(
                            #         [('name', '=', 'Units')],
                            #         limit=1)
                            #     if search_uom:
                            #         tmpl_vals.update(
                            #             {'uom_id': search_uom.id})
                            #     else:
                            #         skipped_line_no[str(
                            #             counter
                            #         )] = " - Unit of Measure - Units not found. "
                            #         counter = counter + 1
                            #         continue
                            # else:
                            #     search_uom = self.env[
                            #         'uom.uom'].search([
                            #         ('name', '=', row[6].strip())
                            #     ],
                            #         limit=1)
                            #     if search_uom:
                            #         tmpl_vals.update(
                            #             {'uom_id': search_uom.id})
                            #     else:
                            #         skipped_line_no[str(
                            #             counter
                            #         )] = " - Unit of Measure not found. "
                            #         counter = counter + 1
                            #         continue
                            #
                            # if row[7].strip() in (None, ""):
                            #     search_uom_po = self.env[
                            #         'uom.uom'].search(
                            #         [('name', '=', 'Units')],
                            #         limit=1)
                            #     if search_uom_po:
                            #         tmpl_vals.update({
                            #             'uom_po_id':
                            #                 search_uom_po.id
                            #         })
                            #     else:
                            #         skipped_line_no[str(
                            #             counter
                            #         )] = " - Purchase Unit of Measure - Units not found. "
                            #         counter = counter + 1
                            #         continue
                            # else:
                            #     search_uom_po = self.env[
                            #         'uom.uom'].search([
                            #         ('name', '=', row[7].strip())
                            #     ],
                            #         limit=1)
                            #     if search_uom_po:
                            #         tmpl_vals.update({
                            #             'uom_po_id':
                            #                 search_uom_po.id
                            #         })
                            #     else:
                            #         skipped_line_no[str(
                            #             counter
                            #         )] = " - Purchase Unit of Measure not found. "
                            #         counter = counter + 1
                            #         continue
                            #
                            # customer_taxes_ids_list = []
                            # some_taxes_not_found = False
                            # if row[8].strip() not in (None, ""):
                            #     for x in row[8].split(','):
                            #         x = x.strip()
                            #         if x != '':
                            #             search_customer_tax = self.env[
                            #                 'account.tax'].search(
                            #                 [('name', '=', x)],
                            #                 limit=1)
                            #             if search_customer_tax:
                            #                 customer_taxes_ids_list.append(
                            #                     search_customer_tax.id)
                            #             else:
                            #                 some_taxes_not_found = True
                            #                 skipped_line_no[str(
                            #                     counter
                            #                 )] = " - Customer Taxes " + x + " not found. "
                            #                 break
                            #
                            # if some_taxes_not_found:
                            #     counter = counter + 1
                            #     continue
                            # else:
                            #     tmpl_vals.update({
                            #         'taxes_id':
                            #             [(6, 0, customer_taxes_ids_list)]
                            #     })
                            #
                            # vendor_taxes_ids_list = []
                            # some_taxes_not_found = False
                            # if row[9].strip() not in (None, ""):
                            #     for x in row[9].split(','):
                            #         x = x.strip()
                            #         if x != '':
                            #             search_vendor_tax = self.env[
                            #                 'account.tax'].search(
                            #                 [('name', '=', x)],
                            #                 limit=1)
                            #             if search_vendor_tax:
                            #                 vendor_taxes_ids_list.append(
                            #                     search_vendor_tax.id)
                            #             else:
                            #                 some_taxes_not_found = True
                            #                 skipped_line_no[str(
                            #                     counter
                            #                 )] = " - Vendor Taxes " + x + " not found. "
                            #                 break
                            #
                            # if some_taxes_not_found:
                            #     counter = counter + 1
                            #     continue
                            # else:
                            #     tmpl_vals.update({
                            #         'supplier_taxes_id':
                            #             [(6, 0, vendor_taxes_ids_list)]
                            #     })
                            #
                            # tmpl_vals.update(
                            #     {'description_sale': row[10]})
                            #
                            # tmpl_vals.update(
                            #     {'invoice_policy': 'order'})
                            # if row[11].strip(
                            # ) == 'Delivered quantities':
                            #     tmpl_vals.update(
                            #         {'invoice_policy': 'delivery'})
                            #
                            # if row[12] not in (None, ""):
                            #     tmpl_vals.update(
                            #         {'list_price': row[12]})
                            #
                            # if row[13] not in (None, ""):
                            #     tmpl_vals.update(
                            #         {'standard_price': row[13]})
                            #
                            # if row[14].strip() in (
                            #         None,
                            #         "") or row[15].strip() in (None,
                            #                                    ""):
                            #
                            #     has_variant = False
                            #     if row[16] not in (None, ""):
                            #         tmpl_vals.update(
                            #             {'default_code': row[16]})
                            #
                            #     if row[17] not in (None, ""):
                            #         tmpl_vals.update(
                            #             {'barcode': row[17]})
                            #
                            #     if row[18] not in (None, ""):
                            #         tmpl_vals.update(
                            #             {'weight': row[18]})
                            #
                            #     if row[19] not in (None, ""):
                            #         tmpl_vals.update(
                            #             {'volume': row[19]})
                            #
                            #     if row[21].strip() not in (None, ""):
                            #         image_path = row[21].strip()
                            #         if "http://" in image_path or "https://" in image_path:
                            #             try:
                            #                 r = requests.get(
                            #                     image_path)
                            #                 if r and r.content:
                            #                     image_base64 = base64.encodebytes(
                            #                         r.content)
                            #                     tmpl_vals.update({
                            #                         'image_1920':
                            #                             image_base64
                            #                     })
                            #                 else:
                            #                     skipped_line_no[str(
                            #                         counter
                            #                     )] = " - URL not correct or check your image size. "
                            #                     counter = counter + 1
                            #                     continue
                            #             except Exception as e:
                            #                 skipped_line_no[str(
                            #                     counter
                            #                 )] = " - URL not correct or check your image size " + ustr(
                            #                     e)
                            #                 counter = counter + 1
                            #                 continue
                            #
                            #         else:
                            #             try:
                            #                 with open(
                            #                         image_path,
                            #                         'rb') as image:
                            #                     image.seek(0)
                            #                     binary_data = image.read(
                            #                     )
                            #                     image_base64 = codecs.encode(
                            #                         binary_data,
                            #                         'base64')
                            #                     if image_base64:
                            #                         tmpl_vals.update({
                            #                             'image_1920':
                            #                                 image_base64
                            #                         })
                            #                     else:
                            #                         skipped_line_no[str(
                            #                             counter
                            #                         )] = " - Could not find the image or please make sure it is accessible to this app. "
                            #                         counter = counter + 1
                            #                         continue
                            #             except Exception as e:
                            #                 skipped_line_no[str(
                            #                     counter
                            #                 )] = " - Could not find the image or please make sure it is accessible to this app. " + ustr(
                            #                     e)
                            #                 counter = counter + 1
                            #                 continue
                            #
                            # else:
                            #     has_variant = True

                            # ===================================================================
                            # Step 1: Search Product Template Here if exist than use it.
                            # Search by name for now.
                            if self.method == 'create':
                                created_leave = leave_obj.create(
                                    tmpl_vals)

                                if is_confirmed:
                                    created_leave.action_confirm()

                                if is_validate1:
                                    created_leave.action_confirm()
                                    created_leave.action_approve()

                                if is_validate:
                                    created_leave.action_confirm()
                                    created_leave.action_validate()

                                if is_refused:
                                    created_leave.action_confirm()
                                    created_leave.action_refuse()

                            elif self.method == 'write':

                                # =====================================
                                # Search or Update product by
                                # =====================================

                                search_product = product_tmpl_obj.search(
                                    running_tmpl_domain, limit=1)

                                # =====================================
                                # Search or Update product by
                                # =====================================

                                if search_product:
                                    # Write product Template Field.
                                    search_product.write(tmpl_vals)
                                    created_product_tmpl = search_product
                                else:
                                    created_product_tmpl = product_tmpl_obj.create(
                                        tmpl_vals)

                            counter = counter + 1

                        except Exception as e:
                            skipped_line_no[str(
                                counter)] = " - Value is not valid. " + ustr(e)
                            counter = counter + 1
                            continue

                    # For Loop Ends here

                except Exception as e:
                    raise UserError(
                        _("Sorry, Your csv or excel file does not match with our format"
                          + ustr(e)))

                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records,
                                                skipped_line_no)
                    return res
