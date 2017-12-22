# -*- coding: utf-8 -*-
from urllib2 import Request, urlopen
from urllib import urlencode
from openerp import api, fields, models
import json
import logging
_logger = logging.getLogger(__name__)

class SmsTemplate(models.Model):
    _name = "sms.template"

    name = fields.Char(required=True, string='Template Name')
    model_id = fields.Many2one('ir.model', string='Applies to', help="name of model, in which this template can be used")
    template_body = fields.Text('Message Body', help="Plain text or HTML message")

class SmsAccount(models.Model):
    _name = "sms.account"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "SMS Account"

    name = fields.Char(string='Account Name', required=True)
    account_uid = fields.Char(string='Account User', required=True)
    account_hashcode = fields.Char(string='Account Hashcode', required=True)
    sender_number = fields.Char(string='Sender', required=True)
    send_url = fields.Char(string='Send URL', required=True)
    api_url = fields.Char(string='API URL')
    history_ids = fields.One2many('sms.message', 'message_account_id', string='Message History')

    @api.multi
    def send_message(self, numbers, sms_content, model, res_id):
        json_data = {}
        sms_msg = False
        message_id = False
        status = False
        for record in self:
            try:
                sms_data = {
                    'username': record.account_uid.replace(" ", ""),
                    'hash': record.account_hashcode.replace(" ", ""),
                    'numbers': numbers,
                    'message': sms_content,
                    'sender': record.sender_number.replace(" ", ""),
                    'unicode': True,
                    }
                try:
                    encode_data = urlencode(sms_data)
                    request = Request(record.send_url.replace(" ", ""))
                    response = urlopen(request, encode_data)
                    json_data = json.loads(response.read())
                except Exception as e:
                    _logger.error("Wrong Textlocal response or json Error\n{}".format(e))
                if json_data:
                    if json_data.get('batch_id'):
                        message_id = json_data.get('batch_id', False)
                    if json_data.get('status'):
                        status = json_data.get('status', False)
                    if self.env.context.get('record_id'):
                        sms_msg = self.env['sms.message'].browse(self.env.context.get('record_id'))
                        sms_msg.status = status
                        sms_msg.message_id = message_id
                        sms_msg.message_date = fields.Datetime.now()
                    else:
                        values = {
                            'message_account_id': record.id,
                            'send_to': numbers,
                            'send_from': record.sender_number.replace(" ", ""),
                            'message_id': message_id,
                            'message_date': fields.Datetime.now(),
                            'status': status,
                            'sms_content': sms_content,
                            'model': model or False,
                            'res_id': res_id or False
                        }
                        if json_data.get('status') != 'success':
                            sms_msg = self.env['sms.message'].create(values)
                    if sms_msg and json_data.get('errors'):
                        sms_msg.message_post(body=json_data['errors'][0].get('message'))
                    if sms_msg and json_data.get('warnings'):
                        warning_msg = "%s: %s" % (json_data['warnings'][0].get('message'), json_data['warnings'][0].get('numbers'))
                        sms_msg.message_post(body=warning_msg)
                    if json_data.get('status') == 'success':
                        _logger.info('SMS with ID %r and Model %r successfully sent', res_id, model)
            except Exception as e:
                _logger.error("Error occurs in sms sending :\n{}".format(e))

class SmsMessage(models.Model):
    _name = "sms.message"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "SMS Message"
    _order = "message_date desc"

    message_account_id = fields.Many2one('sms.account', string='Gateway Account', required=True)
    send_from = fields.Char(string='Send From', required=True)
    send_to = fields.Char(string='Send To', required=True)
    sms_content = fields.Text(string='Content')
    message_date = fields.Datetime('Message Date', readonly=True)
    message_id = fields.Char('Message ID', index=True, readonly=1, copy=False)
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Integer('Related Document ID', index=True)
    status = fields.Char('Status', readonly=True)

    def send_sms_message(self):
        self.ensure_one()
        ctx = dict(record_id=self.id)
        if self.message_account_id:
            to_send = self.send_to
            sms_content = self.sms_content or ''
            model = self.model or False
            res_id = self.res_id or False
            if to_send:
                self.message_account_id.with_context(ctx).send_message(to_send, sms_content, model, res_id)
