# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class HotelReservation(models.Model):
    _inherit = 'hotel.reservation'

    user_id = fields.Many2one('res.users', string='Responsible', required=True, default=lambda self: self.env.uid, help="person responsible for this reservation")

    @api.multi
    def send_reservation_sms(self):
        self.ensure_one()
        sms_account = self.env['sms.account'].search([], limit=1)
        if sms_account:
            for order in self:
                if order.partner_id and order.partner_id.mobile or order.partner_id and order.partner_id.phone:
                    recipent = order.partner_id.mobile or order.partner_id.phone
                    to_mobile = recipent.replace(" ", "")
                    try:
                        res = self.env['sms.template'].search([('model_id', '=', 'hotel.reservation')], limit=1)
                        if res:
                            render_msg = self.env['mail.template'].render_template(res.template_body, 'hotel.reservation', order.id)
                            message = tools.html2plaintext(render_msg)
                            sms_account.send_message(to_mobile, message, self._name, order.id)
                    except Exception as e:
                        _logger.error("Error in reservation sms sending:\n{}".format(e))
                else:
                    raise UserError(_('Configuration error!\n Partner must have mobile number'))
        return True

    @api.multi
    def email_on_confirmation(self):
        self.ensure_one()
        template_rec = False
        for order in self:
            if order.partner_id.email:
                try:
                    template_rec = self.env.ref('odoo_sms_email.hotel_reservation_email_template', False)
                except Exception as e:
                    _logger.error("Error in reservation email template :\n{}".format(e))
                if template_rec:
                    template_rec.send_mail(order.id, force_send=True)
            else:
                raise UserError(_('Configuration error!\n Partner must have email address'))
        return True

    @api.multi
    def confirmed_reservation(self):
        res = super(HotelReservation, self).confirmed_reservation()
        for order in self:
            order.send_reservation_sms()
            order.email_on_confirmation()
        return res

class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    @api.multi
    def send_hotel_folio_sms(self):
        self.ensure_one()
        sms_account = self.env['sms.account'].search([], limit=1)
        if sms_account:
            for order in self:
                if order.partner_id and order.partner_id.mobile or order.partner_id and order.partner_id.phone:
                    recipent = order.partner_id.mobile or order.partner_id.phone
                    to_mobile = recipent.replace(" ", "")
                    try:
                        hotel = self.env['sms.template'].search([('model_id', '=', 'hotel.folio')], limit=1)
                        if hotel:
                            render_msg = self.env['mail.template'].render_template(hotel.template_body, 'hotel.folio', order.id, post_process=True)
                            message = tools.html2plaintext(render_msg)
                            sms_account.send_message(to_mobile, message, self._name, order.id)
                    except Exception as e:
                        _logger.error("Error in hotel folio sms sending :\n{}".format(e))
                else:
                    raise UserError(_('Configuration error!\n Partner must have mobile number'))
        return True

    @api.multi
    def send_email_on_confirm(self):
        self.ensure_one()
        template_rec = False
        for order in self:
            if order.partner_id.email:
                try:
                    template_rec = self.env.ref('odoo_sms_email.hotel_folio_email_template', False)
                except Exception as e:
                    _logger.error("Error in hotel folio email template :\n{}".format(e))
                if template_rec:
                    template_rec.send_mail(order.id, force_send=True)
            else:
                raise UserError(_('Configuration error!\n Partner must have email address'))
        return True

    @api.multi
    def action_confirm(self):
        res = super(HotelFolio, self).action_confirm()
        for hotel in self:
            hotel.send_hotel_folio_sms()
            hotel.send_email_on_confirm()
        return res
