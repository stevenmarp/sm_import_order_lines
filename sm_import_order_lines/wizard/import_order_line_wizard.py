import base64
import csv
import io

from odoo import _, api, fields, models
from odoo.exceptions import UserError


def read_rows(datas, filename):
    """Return a list of row lists from a CSV or XLSX file (base64 datas)."""
    content = base64.b64decode(datas or b"")
    rows = []
    if filename and filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig", errors="ignore")
        for r in csv.reader(io.StringIO(text)):
            if any((c or "").strip() for c in r):
                rows.append([(c or "").strip() for c in r])
    else:
        try:
            import openpyxl
        except ImportError:
            raise UserError(_("The openpyxl python library is required to import Excel files. Use a CSV file instead."))
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        for row in ws.iter_rows(values_only=True):
            if row and any(c is not None and str(c).strip() for c in row):
                rows.append(["" if c is None else c for c in row])
    return rows


class ImportOrderLineWizard(models.TransientModel):
    _name = "sm.import.order.line.wizard"
    _description = "Import Sale Order Lines"

    order_id = fields.Many2one("sale.order", string="Sale Order", required=True)
    import_file = fields.Binary(string="File", required=True)
    file_name = fields.Char(string="File Name")
    match_by = fields.Selection(
        [("code", "Internal Reference"), ("barcode", "Barcode"), ("name", "Product Name")],
        string="Match Product By", default="code", required=True,
    )
    has_header = fields.Boolean(string="File Has Header Row", default=True)
    create_missing = fields.Boolean(string="Create Missing Products (by name)")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get("active_model") == "sale.order" and self.env.context.get("active_id"):
            res["order_id"] = self.env.context["active_id"]
        return res

    def _find_product(self, key):
        key = str(key).strip()
        Product = self.env["product.product"]
        if self.match_by == "code":
            product = Product.search([("default_code", "=", key)], limit=1)
        elif self.match_by == "barcode":
            product = Product.search([("barcode", "=", key)], limit=1)
        else:
            product = Product.search([("name", "=", key)], limit=1)
            if not product and self.create_missing:
                product = Product.create({"name": key})
        return product

    def action_import(self):
        self.ensure_one()
        rows = read_rows(self.import_file, self.file_name)
        if self.has_header and rows:
            rows = rows[1:]
        if not rows:
            raise UserError(_("The file has no data rows."))
        Line = self.env["sale.order.line"]
        created = Line
        for idx, row in enumerate(rows, start=1):
            if not row or not str(row[0]).strip():
                continue
            product = self._find_product(row[0])
            if not product:
                raise UserError(_("Row %s: no product found for '%s'.") % (idx, row[0]))
            vals = {"order_id": self.order_id.id, "product_id": product.id}
            if len(row) > 1 and str(row[1]).strip():
                vals["product_uom_qty"] = float(row[1])
            if len(row) > 2 and str(row[2]).strip():
                vals["price_unit"] = float(row[2])
            if len(row) > 3 and str(row[3]).strip():
                vals["name"] = str(row[3])
            created |= Line.create(vals)
        return {"type": "ir.actions.act_window_close"}
