# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, tools
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    _description = "Point of Sale Orders"

    @api.multi
    def send_pos_message(self):
        try:
            sms_account = self.env['sms.account'].search([], limit=1)
            pos_order = self.env['sms.template'].search([('model_id', '=', 'pos.order')], limit=1)
            if pos_order and sms_account:
                for order in self:
                    if order.partner_id and order.partner_id.mobile or order.partner_id and order.partner_id.phone:
                        number = order.partner_id.mobile or order.partner_id.phone
                        to_mobile = number.replace(" ", "")
                        render_msg = self.env['mail.template'].render_template(pos_order.template_body, 'pos.order', order.id)
                        message = tools.html2plaintext(render_msg)
                        sms_account.send_message(to_mobile, message, self._name, order.id)
        except Exception as e:
            _logger.error("Error in pos sms template :\n{}".format(e))
        return True

    @api.model
    def create_from_ui(self, orders):
        order_ids = super(PosOrder, self).create_from_ui(orders)
        for order_id in order_ids:
            pos_order = self.browse(order_id)
            if pos_order and pos_order.partner_id:
                pos_order.send_pos_message()
        return order_ids
