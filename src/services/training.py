import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import logging

from src.services.ewma import compute_ewma_with_state
from src.core.settings import get_db_connection
import uuid
from datetime import datetime


uuid.uuid4()
now = datetime.utcnow()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_training_pipeline():
    try:
        logger.info("Iniciando pipeline de treinamento EWMA...")
        conn = get_db_connection()
        cur = conn.cursor()

        logger.info("Buscando transações com estado 'PURCHASED' ou 'IN_PANTRY'...")
        cur.execute("""
            SELECT user_id, product_id, portion, portion_type, created_at, state
            FROM item_transaction
            WHERE state IN ('PURCHASED', 'IN_PANTRY')
        """)
        rows = cur.fetchall()

        if not rows:
            logger.warning("Nenhuma transação encontrada para estados considerados.")
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=["user_id", "product_id", "portion", "portion_type", "created_at", "state"])
        df["created_at"] = pd.to_datetime(df["created_at"])

        logger.info("Calculando scores de recorrência com EWMA...")
        results = compute_ewma_with_state(df)

        logger.info(f"Inserindo {len(results)} resultados na tabela product_recurrence_score...")

        insert_query = '''
           INSERT INTO product_recurrence_score (
                id, user_id, product_id, recurrence_score,
                ewma_latest, ewma_avg, total_logs, states_considered, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, product_id)
            DO UPDATE SET
                recurrence_score = EXCLUDED.recurrence_score,
                ewma_latest = EXCLUDED.ewma_latest,
                ewma_avg = EXCLUDED.ewma_avg,
                total_logs = EXCLUDED.total_logs,
                states_considered = EXCLUDED.states_considered,
                updated_at = EXCLUDED.updated_at;
        '''
        data = [
            (
                str(uuid.uuid4()),
                row["user_id"], row["product_id"], row["recurrence_score"],
                row["ewma_latest"], row["ewma_avg"],
                row["total_logs"], row["states_considered"], now
            )
            for _, row in results.iterrows()
        ]

        execute_batch(cur, insert_query, data)
        conn.commit()

        logger.info("Pipeline de treinamento concluída com sucesso.")
        return results

    except psycopg2.Error as e:
        logger.exception("Erro de banco de dados durante a execução da pipeline.")
        raise

    except Exception as e:
        logger.exception("Erro inesperado durante a execução da pipeline.")
        raise

    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except Exception as e:
            logger.warning("Erro ao fechar conexão com o banco.")
