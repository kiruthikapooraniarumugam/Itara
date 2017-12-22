# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
import logging
_logger = logging.getLogger(__name__)

class SendMassMessage(models.TransientModel):
    _name = "send.mass.message"
    _description = "Send Mass Message"

    message_text = fields.Text(string='Message', required=True)

    @api.multi
    def mass_message_send(self):
        message = ''
        content = ''
        render_msg = False
        context = dict(self._context or {})
        if context.get('active_model') == 'res.partner' and context.get('active_ids'):
            active_ids = context.get('active_ids', []) or []
            active_model = context.get('active_model') or False
            sms_account = self.env['sms.account'].search([], limit=1)
            if sms_account:
                try:
                    render_msg = self.env['mail.template'].render_template(self.message_text, 'res.partner', active_ids)
                    if render_msg:
                        content = render_msg.values()[0] or ''
                    message = tools.html2plaintext(content)
                except Exception as e:
                    _logger.error("Error in mass sms sending: \n{}".format(e))
                for record in self.env['res.partner'].browse(active_ids):
                    if record.mobile or record.phone:
                        number = record.mobile or record.phone
                        to_mobile = number.replace(" ", "")
                        sms_account.send_message(to_mobile, message, active_model, record)
        return {'type': 'ir.actions.act_window_close'}
