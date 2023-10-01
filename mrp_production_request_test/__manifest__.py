{
    "name": "MRP Production Request Test",
    "summary": "Allows you to use Manufacturing Request as a previous "
    "step to Manufacturing Orders for better manufacture "
    "planification.",
    "version": "15.0.1.0.1",
    "development_status": "Production/Stable",
    "category": "Manufacturing",
    "author": "Odoo Bangladesh",
    "license": "LGPL-3",
    "depends": [
            "mrp"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/aa_line_view.xml",
        # "wizards/production_request_create_mo_view.xml",
        "wizards/add_production_request_view.xml",
        "views/mrp_production_request_view.xml",
    ],
    "application": False,
    "installable": True,
}
