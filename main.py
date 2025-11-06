from fastapi import FastAPI, Request, Depends, Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

from database import SessionLocal, SurveyManager, create_db_and_tables
from telegram_sender import TelegramSender

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria o app FastAPI
app = FastAPI(title="API de Pesquisa UNIRIO via Telegram")

# Cria as tabelas do banco de dados na inicialização
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Modelos Pydantic (Sem mudanças) ---
class Chat(BaseModel):
    id: int
class Message(BaseModel):
    chat: Chat
    text: Optional[str]
class TelegramUpdate(BaseModel):
    message: Message

# --- Dependências (Sem mudanças) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Instâncias e Perguntas (Sem mudanças) ---
telegram_client = TelegramSender()

Q1 = "Qual o seu vínculo principal com a UNIRIO?"
Q2 = "Se você fosse o conselheiro do nosso Reitor por um dia, qual sugestão você daria para melhorar a UNIRIO?"

MSG_NO_SURVEY = "Olá! Envie /iniciar para começar uma nova pesquisa."

MSG_THANKS = "Obrigado por suas respostas! Sua contribuição é muito valiosa para o nosso Trabalho."

MSG_TERMS = """Antes de começar você precisa estar ciente esta conversa é na 
verdade uma pesquisa que faz parte de um projeto de pesquisa 
que visa identificar e categorizar as principais oportunidades 
de melhoria em nossa universidade, sob a perspectiva de quem 
vivencia a UNIRIO todos os dias.""" 

# --- Rota Raiz ---
@app.get("/")
def read_root():
    return {"status": "live"}


# --- Rota do Webhook ---
@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate, db: Session = Depends(get_db)):
    """
    Endpoint que recebe as atualizações (mensagens) do Telegram.
    """
    if not update.message or not update.message.text:
        return Response(status_code=200) # Ignora mensagens sem texto

    user_chat_id = update.message.chat.id
    user_message = update.message.text
    
    survey_manager = SurveyManager(db)
    reply_message = ""



    # 1. O comando /start SEMPRE inicia uma nova pesquisa
    if user_message.lower() == "/iniciar":
        survey_manager.start_survey(user_chat_id)
        reply_message = Q1

        telegram_client.send_message(user_chat_id, MSG_TERMS)
    
    else:
        # 2. Se não for /start, procuramos uma pesquisa ATIVA
        user_state = survey_manager.get_active_survey(user_chat_id)

        if user_state is None:
            # 3. Se não há pesquisa ativa, e não foi /start, instruímos o usuário a iniciar uma nova pesquisa.
            reply_message = MSG_NO_SURVEY

        elif user_state.status == "started":
            # 4. Usuário está respondendo a Q1 da pesquisa ativa
            survey_manager.save_answer(user_chat_id, user_message, "started")
            reply_message = Q2

        elif user_state.status == "q1_answered":
            # 5. Usuário está respondendo a Q2 da pesquisa ativa
            survey_manager.save_answer(user_chat_id, user_message, "q1_answered")
            reply_message = MSG_THANKS
            # (A pesquisa agora está marcada como 'completed' no banco
            # e não será encontrada por 'get_active_survey' da próxima vez)

    # Enviar a resposta de volta ao usuário
    if reply_message:
        telegram_client.send_message(user_chat_id, reply_message)

    # Retornar 200 OK para o Telegram
    return Response(status_code=200)


@app.get("/export")
def export_responses(db: Session = Depends(get_db)):
    """
    Exporta todas as respostas da pesquisa armazenadas no banco de dados.
    """
    survey_manager = SurveyManager(db)
    all_responses = survey_manager.export()
    
    return all_responses