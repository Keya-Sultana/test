# -*- coding: utf-8 -*-

{
    "name": "Import Leave / Holiday from CSV/Excel file - Advance",
    "author": "Binary Quest Limited",
    'website': 'www.odoo.com.bd',
    "support": "support@binaryquest.com",
    "license": "OPL-1",
    "category": "Extra Tools",
    "summary":
    "Import Leave From CSV Import Leave Excel Import Leave XLS Import Leave From XLSX Leave From Excel Leave CSV Import Leave E Commerce Odoo",
    "description":
    """Do you want to import products with product variants From CSV/Excel? This module helps to import products with product variants from the CSV or Excel files. This module provides a facility to import custom fields also. Here you can create or update product variants(image, price, color, size) from CSV/Excel.
Import Product variants From CSV/Excel Odoo,Import Product Variant From CSV,  Import Product Variant From Excel,Import  Product Variant From XLS, Import  Product Variant From XLSX Moule, Import Variants From Excel, Import Variant From CSV, Import Variant From XLS Odoo
  Import Product Variant From CSV,  Import  Product Variant Excel App,Import  Product Variant XLS, Import  Product Variant From XLSX Moule, Product Variant From Excel,  Product Variant From CSV,  Product Variant From XLS,  Product Variant From XLSX Odoo """,
    "version": "1.0.2",
    "depends": ["hr_holidays", "sh_message"],
    "application": True,
    "data": [
        "security/import_leave_security.xml",
        "security/ir.model.access.csv",
        "wizard/import_leave_wizard.xml",
        "views/menu_view.xml",
    ],
    "external_dependencies": {
        "python": ["xlrd"],
    },
    "images": [
        "static/description/background.png",
    ],
    "auto_install": False,
    "installable": True
}
