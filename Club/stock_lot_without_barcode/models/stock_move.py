# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.onchange('lot_name', 'lot_id')
    def onchange_serial_number(self):
        lot_id = self.env['stock.production.lot']
        res = super(StockMoveLine, self).onchange_serial_number()
        if self.picking_id and self.picking_id.picking_type_id and self.picking_id.picking_type_id.use_existing_lots and self.lot_name:
            lot_id = self.env['stock.production.lot'].search([('product_id', '=', self.product_id.id), ('name', '=', self.lot_name)], limit=1)
            if not lot_id and self.picking_id and self.picking_id.picking_type_id and self.picking_id.picking_type_id.use_create_lots:
                lot_id = self.env['stock.production.lot'].create({'name': self.lot_name, 'product_id': self.product_id.id})
            if not lot_id:
                raise UserError(_('Lot/Serial not found !'))
            if lot_id:
                available_qty = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, lot_id, self.package_id, self.owner_id, False, False)
                if available_qty > 0:
                    self.lot_id = lot_id and lot_id.id or False
                else:
                    res['warning'] = {'title': _('Warning'), 'message': 'Available qty for this product is %s' % available_qty}
        return res

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        res = {}
        if self.lot_id and self.qty_done:
            available_qty = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, self.package_id, self.owner_id, False, False)
            if self.qty_done > available_qty:
                res['warning'] = {'title': _('Warning'), 'message': 'Available qty for this product is %s' % available_qty}
        return res

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)
        if res.state in ('partially_available', 'confirmed', 'assigned') and res.product_id.type == 'product':
            res.move_id._update_reserved_quantity(res.move_id.product_uom_qty, res.qty_done, res.location_id, res.lot_id, res.package_id, res.owner_id, strict=True)
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        if res:
            res['context']['show_lots_text'] = self.has_tracking != 'none' and self.picking_type_id.use_create_lots or self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id
        return res
