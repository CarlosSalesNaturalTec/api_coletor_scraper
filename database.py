import os
from google.cloud import firestore
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

_db = None

def get_db():
    """
    Inicializa e retorna um cliente Firestore, garantindo uma instância única.
    """
    global _db
    if _db is None:
        try:
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                raise ValueError("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não está definida.")
            
            _db = firestore.Client()
        except Exception as e:
            print(f"Erro ao conectar ao Firestore: {e}")
            return None
    return _db

def save_error_log(error_message, context=None):
    """Salva uma mensagem de erro na coleção 'erros_de_execucao'."""
    db = get_db()
    if not db:
        print("Não foi possível salvar o log de erro: sem conexão com o banco de dados.")
        return

    try:
        log_data = {
            'message': error_message,
            'context': context,
            'timestamp': datetime.now()
        }
        db.collection('erros_de_execucao').add(log_data)
    except Exception as e:
        print(f"Erro ao salvar log de erro no Firestore: {e}")
