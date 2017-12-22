# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, tools
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def send_account_invoice_sms(self):
        message = ''
        try:
            sms_account = self.env['sms.account'].search([], limit=1)
            template_rec = self.env['sms.template'].search([('model_id', '=', 'account.invoice')], limit=1)
            if sms_account and template_rec:
                for invoice in self:
                    if invoice.partner_id and invoice.partner_id.mobile or invoice.partner_id and invoice.partner_id.phone:
                        number = invoice.partner_id.mobile or invoice.partner_id.phone
                        to_mobile = number.replace(" ", "")
                        render_msg = self.env['mail.template'].render_template(template_rec.template_body, 'account.invoice', invoice.id)
                        message = tools.html2plaintext(render_msg)
                        sms_account.send_message(to_mobile, message, self._name, invoice.id)
        except Exception as e:
            _logger.error("Error in invoice sms template:\n{}".format(e))
        return True

    @api.multi
    def email_on_validation(self):
        template_rec = False
        try:
            template_rec = self.env.ref('odoo_sms_email.email_on_invoice_validation', False)
            if template_rec:
                for invoice in self:
                    if invoice.partner_id.email:
                        template_rec.send_mail(invoice.id, force_send=True)
        except Exception as e:
            _logger.error("Error in account invoice email template :\n{}".format(e))
        return True

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            invoice.send_account_invoice_sms()
            if invoice.origin:
                if 'BAR' in invoice.origin:
                    print "BAR"
                elif 'Chamber' in invoice.origin:
                    print "chamber"
                elif 'Dinning' in invoice.origin:
                    print "dining"
                elif 'Main' in invoice.origin:
                    print "main"
                else:
                    invoice.email_on_validation()
            else:
                invoice.email_on_validation()
        return res
