import os
from twilio.rest import Client

class TwilioSender:
    """
    Classe wrapper para enviar mensagens de WhatsApp usando a API do Twilio.
    """
    def __init__(self):
        # Pega as credenciais das variáveis de ambiente
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.twilio_phone_number]):
            raise ValueError("As variáveis de ambiente do Twilio não estão configuradas!")
            
        self.client = Client(self.account_sid, self.auth_token)

    def send_whatsapp_message(self, to_number: str, message: str):
        """
        Envia uma mensagem de WhatsApp para um número de destino.
        
        Args:
            to_number (str): O número do destinatário (formato: whatsapp:+5521999998888).
            message (str): O conteúdo da mensagem a ser enviada.
        """
        try:
            self.client.messages.create(
                from_=f'whatsapp:{self.twilio_phone_number}',
                body=message,
                to=to_number
            )
            print(f"Mensagem enviada para {to_number}: '{message}'")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {to_number}: {e}")