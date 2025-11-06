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


class SurveyResponse(Base):
    """Cria a tabela de survey onde todas as respostas serão armazenadas"""
    __tablename__ = "survey_responses"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True) 
    status = Column(String, default="started")
    question_1_answer = Column(String, nullable=True)
    question_2_answer = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_db_and_tables():
    """Cria o arquivo do banco de dados e a tabela se não existirem."""
    Base.metadata.create_all(bind=engine)


class SurveyManager:
    """
    Gerencia o estado e as respostas da pesquisa no banco de dados.
    é a casse responsável por manipular o banco.
    """
    def __init__(self, db_session):
        self.db = db_session

    def get_active_survey(self, chat_id: int):
        """
        Encontra a pesquisa mais recente deste usuário que não está 
        marcada como 'completed'.
        """
        return self.db.query(SurveyResponse).filter(
            SurveyResponse.chat_id == chat_id,
            SurveyResponse.status != "completed"
        ).order_by(SurveyResponse.created_at.desc()).first()

    def start_survey(self, chat_id: int):
        """
        Inicia uma nova pesquisa para um usuário, sempre criando um novo registro.
        """
        new_response = SurveyResponse(chat_id=chat_id)
        self.db.add(new_response)
        self.db.commit()
        self.db.refresh(new_response)
        return new_response

    def save_answer(self, chat_id: int, answer: str, current_status: str):
        """
        Salva a resposta do usuário na sua pesquisa ativa.
        """
        user_response = self.get_active_survey(chat_id)
        if not user_response:
            return None 

        if current_status == "started":
            user_response.question_1_answer = answer
            user_response.status = "q1_answered"
        elif current_status == "q1_answered":
            user_response.question_2_answer = answer
            user_response.status = "completed" # Marca como concluída
        
        self.db.commit()
        self.db.refresh(user_response)
        return user_response
    
    def export(self):
        """
        Exporta todas as respostas da tabela SurveyResponse.
        """
        return self.db.query(SurveyResponse).all()