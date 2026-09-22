from django.conf import settings
from sms_ir import SmsIr


class SMS(SmsIr):
    def __init__(self, api_key=None, template_id=None, linenumber=None):
        super().__init__(
            api_key or settings.SMS_API_KEY,
            linenumber or settings.SMS_LINE_NUMBER,
        )
        self.template_id: int = template_id or settings.SMS_TEMPLATE_ID
    
    def __str__(self):
        return f'SMS template: {self.template_id}'
    
    def send_code(self, number, code):
        params = [{"name": 'code', 'value': code}]
        status = self.send_verify_code(number=number,
                              template_id=self.template_id,
                              parameters=params)
        return status
    
    # def send_status(self, number, orderID, status):
    #     params = [{"name": 'orderid', 'value': orderID}, {"name": 'status', 'value': status}]
    #     status = self.send_verify_code(number=number,
    #                           template_id='620612',
    #                           parameters=params)
    #     print(status)
    #     return status