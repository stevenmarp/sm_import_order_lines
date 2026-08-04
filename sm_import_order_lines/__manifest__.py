{
    "name": "Import Sale Order Lines from Excel/CSV",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Bulk import sale order lines from an Excel or CSV file",
    "description": """
Import Sale Order Lines from Excel/CSV
======================================

Add many sale order lines at once by uploading an Excel or CSV file. Match products
by internal reference, barcode or name, with quantity, price, description and tax.
    """,
    "author": "Steven Marp",
    "website": "https://apps.odoo.com/apps/modules/browse?author=Steven Marp",
    "license": "OPL-1",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_order_line_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": ["static/description/banner.gif", "static/description/icon.png"],
    "price": 10.00,
    "currency": "USD",
}
