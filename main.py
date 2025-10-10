from fastapi import FastAPI, Form, Depends, Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import SessionLocal, SurveyManager, create_db_and_tables
from twilio_sender import TwilioSender

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria o app FastAPI
app = FastAPI(title="API de Pesquisa UNIRIO via WhatsApp")

# Cria as tabelas do banco de dados na inicialização
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Dependências ---
def get_db():
    """Função para injetar a sessão do banco de dados nas rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Instâncias dos nossos serviços ---
twilio_client = TwilioSender()

# --- Perguntas da Pesquisa ---
Q1 = "Qual o seu vínculo principal com a UNIRIO?"
Q2 = "Se você fosse o conselheiro do nosso Reitor por um dia, qual sugestão você daria para melhorar a UNIRIO?"
MSG_COMPLETED = "Você já respondeu a esta pesquisa. Agradecemos sua participação!"
MSG_THANKS = "Obrigado por suas respostas! Sua contribuição é muito valiosa para a UNIRIO."


# --- Rota Raiz (Health Check) ---
@app.get("/")
def read_root():
    """Retorna um status 'live' para indicar que a API está funcionando."""
    return {"status": "live"}


# --- Rota do Webhook ---
@app.post("/webhook/twilio")
def twilio_webhook(
    response: Response,
    From: str = Form(...), 
    Body: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    Endpoint que recebe as mensagens do WhatsApp via webhook do Twilio.
    """
    user_phone_number = From
    user_message = Body
    
    survey_manager = SurveyManager(db)
    user_state = survey_manager.get_user_state(user_phone_number)

    # Lógica principal da conversa
    if user_state is None:
        # 1. Usuário Novo: Inicia a pesquisa e faz a primeira pergunta
        survey_manager.start_survey(user_phone_number)
        twilio_client.send_whatsapp_message(user_phone_number, Q1)
        
    elif user_state.status == "started":
        # 2. Usuário respondeu à Q1: Salva a resposta e faz a Q2
        survey_manager.save_answer(user_phone_number, user_message, "started")
        twilio_client.send_whatsapp_message(user_phone_number, Q2)

    elif user_state.status == "q1_answered":
        # 3. Usuário respondeu à Q2: Salva a resposta e agradece
        survey_manager.save_answer(user_phone_number, user_message, "q1_answered")
        twilio_client.send_whatsapp_message(user_phone_number, MSG_THANKS)
        
    elif user_state.status == "completed":
        # 4. Usuário já completou: Informa que não pode responder de novo
        twilio_client.send_whatsapp_message(user_phone_number, MSG_COMPLETED)

    # Retorna uma resposta vazia com status 204 para o Twilio
    response.status_code = 204
    return response