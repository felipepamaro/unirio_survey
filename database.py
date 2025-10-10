import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# --- Configuração do Banco de Dados ---
DATABASE_URL = "sqlite:///./survey.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Modelo da Tabela ---
class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    status = Column(String, default="started")  # Status: started, q1_answered, completed
    question_1_answer = Column(String, nullable=True)
    question_2_answer = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_db_and_tables():
    """Cria o arquivo do banco de dados e a tabela se não existirem."""
    Base.metadata.create_all(bind=engine)

# --- Classe de Gerenciamento da Pesquisa ---
class SurveyManager:
    """
    Gerencia o estado e as respostas da pesquisa no banco de dados.
    """
    def __init__(self, db_session):
        self.db = db_session

    def get_user_state(self, phone_number: str):
        """Consulta um usuário e retorna seu registro ou None se não existir."""
        return self.db.query(SurveyResponse).filter(SurveyResponse.phone_number == phone_number).first()

    def start_survey(self, phone_number: str):
        """Inicia a pesquisa para um novo número, criando um registro."""
        # Verifica se já não existe, embora a lógica principal deva fazer isso.
        existing_user = self.get_user_state(phone_number)
        if existing_user:
            return existing_user
        
        new_response = SurveyResponse(phone_number=phone_number)
        self.db.add(new_response)
        self.db.commit()
        self.db.refresh(new_response)
        return new_response

    def save_answer(self, phone_number: str, answer: str, current_status: str):
        """Salva a resposta do usuário com base no status atual."""
        user_response = self.get_user_state(phone_number)
        if not user_response:
            return None # Não deveria acontecer na lógica principal

        if current_status == "started":
            user_response.question_1_answer = answer
            user_response.status = "q1_answered"
        elif current_status == "q1_answered":
            user_response.question_2_answer = answer
            user_response.status = "completed"
        
        self.db.commit()
        self.db.refresh(user_response)
        return user_response