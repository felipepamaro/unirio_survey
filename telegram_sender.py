import os
import httpx

class TelegramSender:
    """
    Classe wrapper para enviar mensagens usando a API de Bot do Telegram.
    """
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("A variável de ambiente TELEGRAM_BOT_TOKEN não está configurada!")
            
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.client = httpx.Client()

    def send_message(self, chat_id: int, message: str):
        """
        Envia uma mensagem de texto para um chat_id específico do Telegram.
        
        Args:
            chat_id (int): O ID do chat do usuário.
            message (str): O conteúdo da mensagem a ser enviada.
        """
        endpoint = f"{self.api_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        try:
            response = self.client.post(endpoint, json=payload)
            response.raise_for_status() #controla o erro caso a API falhe.
            print(f"Mensagem enviada para {chat_id}: '{message}'")
        except httpx.HTTPStatusError as e:
            print(f"Erro ao enviar mensagem para {chat_id}: {e.response.text}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para {chat_id}: {e}")

    def __del__(self):
        # Garante que o cliente httpx seja fechado corretamente
        if hasattr(self, 'client'):
            self.client.close()