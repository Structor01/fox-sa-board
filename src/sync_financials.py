#!/usr/bin/env python3
"""
sync_financials.py

Sincroniza coleções financeiras do MongoDB para PostgreSQL, incluindo isForecast e orders como JSON.
Adaptado para ser usado como função no dashboard Streamlit.
"""
import json
import psycopg2
from pymongo import MongoClient
from psycopg2.extras import execute_values

# Importação robusta do BSON para compatibilidade com diferentes versões
try:
    from bson import ObjectId
except ImportError:
    try:
        from bson.objectid import ObjectId
    except ImportError:
        from pymongo.objectid import ObjectId

from datetime import datetime, timezone, timedelta
import streamlit as st

# --- Configurações de conexão ---
PG_CONFIG = {
    "host": "24.199.75.66",
    "port": 5432,
    "user": "myuser",
    "password": "mypassword",
    "database": "mydb"
}
MONGO_URI = (
    "mongodb+srv://doadmin:5vk9a08N2tX3e64U@"
    "foxdigital-e8bf0024.mongo.ondigitalocean.com/admin?"
    "authSource=admin&replicaSet=foxdigital"
)

# --- Utilitários ---
def safe_val(val):
    """Converte ObjectId ou dict para string, ou retorna valor original."""
    if isinstance(val, (dict, ObjectId)):
        return str(val)
    return val

def parse_date(date_str):
    """Converte string YYYYMMDDHHMMSS ou YYYYMMDD para datetime com timezone BRT."""
    if not date_str:
        return None
    if len(date_str) >= 14:
        part = date_str[:14]
    else:
        part = date_str.ljust(14, '0')
    dt = datetime.strptime(part, "%Y%m%d%H%M%S")
    return dt.replace(tzinfo=timezone(timedelta(hours=-3)))

def executar_sincronizacao_financeira():
    """
    Executa a sincronização completa dos dados financeiros do MongoDB para PostgreSQL.
    Retorna um dicionário com o status e logs da operação.
    """
    logs = []
    status = "success"
    
    try:
        logs.append("[start] Iniciando sincronização financeira...")
        
        # Conectar ao MongoDB e PostgreSQL
        client = MongoClient(MONGO_URI)
        pg_conn = psycopg2.connect(**PG_CONFIG)
        logs.append("[info] Conexões com MongoDB e PostgreSQL estabelecidas.")
        
        # Recria tabela finances
        with pg_conn:
            with pg_conn.cursor() as cur:
                logs.append("[step] Recriando tabela 'finances'...")
                cur.execute("DROP TABLE IF EXISTS finances CASCADE;")
                cur.execute("""
                    CREATE TABLE finances (
                        id TEXT PRIMARY KEY,
                        date TIMESTAMPTZ,
                        name TEXT,
                        value NUMERIC,
                        category TEXT,
                        account_id TEXT,
                        orders JSONB,
                        is_forecast BOOLEAN
                    );
                """)
                pg_conn.commit()
        logs.append("[info] Tabela 'finances' recriada com coluna JSONB 'orders'.")
        
        # Sincroniza finances
        logs.append("[step] Sincronizando documentos de 'finances'...")
        db = client['fox']
        fin_docs = list(db.finances.find({"$or": [{"isIgnored": None}, {"isIgnored": False}]}))
        logs.append(f"[info] {len(fin_docs)} documentos lidos de 'finances'.")
        
        fin_records = []
        for doc in fin_docs:
            # extrai lista de orders e converte para JSON
            orders_list = [str(o) for o in doc.get("orders", [])]
            orders_json = json.dumps(orders_list)
            rec = (
                safe_val(doc.get("_id")),
                parse_date(doc.get("date")),
                safe_val(doc.get("name")),
                doc.get("value"),
                safe_val(doc.get("category")),
                safe_val(doc.get("account_id")),
                orders_json,
                bool(doc.get("isForecast", False))
            )
            fin_records.append(rec)
        
        logs.append(f"[info] Preparados {len(fin_records)} registros para inserção.")
        
        insert_fin = """
            INSERT INTO finances (id, date, name, value, category, account_id, orders, is_forecast)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
              date = EXCLUDED.date,
              name = EXCLUDED.name,
              value = EXCLUDED.value,
              category = EXCLUDED.category,
              account_id = EXCLUDED.account_id,
              orders = EXCLUDED.orders,
              is_forecast = EXCLUDED.is_forecast;
        """
        
        with pg_conn:
            with pg_conn.cursor() as cur:
                execute_values(cur, insert_fin, fin_records)
                pg_conn.commit()
        logs.append("[info] Sincronização de 'finances' concluída.")
        
        # Sincroniza finances_categories
        logs.append("[step] Sincronizando 'finances_categories'...")
        
        # Criar tabela se não existir
        with pg_conn:
            with pg_conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS finances_categories (
                        id TEXT PRIMARY KEY,
                        category TEXT,
                        item TEXT,
                        type TEXT,
                        dfc TEXT,
                        dfc_equal TEXT
                    );
                """)
                pg_conn.commit()
        
        cat_docs = list(db.finances_categories.find())
        logs.append(f"[info] {len(cat_docs)} documentos lidos.")
        
        cat_records = [(
            safe_val(d.get("_id")),
            safe_val(d.get("category")),
            safe_val(d.get("item")),
            safe_val(d.get("type")),
            safe_val(d.get("dfc")),
            safe_val(d.get("dfcEqual"))
        ) for d in cat_docs]
        
        logs.append(f"[info] Preparados {len(cat_records)} registros para inserção.")
        
        insert_cat = """
            INSERT INTO finances_categories (id, category, item, type, dfc, dfc_equal)
            VALUES %s
            ON CONFLICT (id) DO NOTHING;
        """
        
        with pg_conn:
            with pg_conn.cursor() as cur:
                execute_values(cur, insert_cat, cat_records)
                pg_conn.commit()
        logs.append("[info] Sincronização de 'finances_categories' concluída.")
        
        # Sincroniza finance_accounts
        logs.append("[step] Sincronizando 'finance_accounts'...")
        
        # Criar tabela se não existir
        with pg_conn:
            with pg_conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS finance_accounts (
                        id TEXT PRIMARY KEY,
                        account TEXT,
                        bank_bank TEXT,
                        bank_number TEXT,
                        value NUMERIC,
                        company_name TEXT,
                        company_cnpj TEXT
                    );
                """)
                pg_conn.commit()
        
        acc_docs = list(db.finance_accounts.find())
        logs.append(f"[info] {len(acc_docs)} documentos lidos.")
        
        acc_records = [(
            safe_val(d.get("_id")),
            safe_val(d.get("account")),
            safe_val(d.get("bank",{}).get("bank")),
            safe_val(d.get("bank",{}).get("number")),
            d.get("value"),
            safe_val(d.get("company",{}).get("name")),
            safe_val(d.get("company",{}).get("cnpj"))
        ) for d in acc_docs]
        
        logs.append(f"[info] Preparados {len(acc_records)} registros para inserção.")
        
        insert_acc = """
            INSERT INTO finance_accounts (id, account, bank_bank, bank_number, value, company_name, company_cnpj)
            VALUES %s
            ON CONFLICT (id) DO NOTHING;
        """
        
        with pg_conn:
            with pg_conn.cursor() as cur:
                execute_values(cur, insert_acc, acc_records)
                pg_conn.commit()
        logs.append("[info] Sincronização de 'finance_accounts' concluída.")
        
        # Encerramento
        pg_conn.close()
        client.close()
        logs.append("[end] Sincronização finalizada e conexões fechadas.")
        
    except Exception as e:
        status = "error"
        logs.append(f"[error] Erro durante sincronização: {str(e)}")
    
    return {
        "status": status,
        "logs": logs,
        "total_logs": len(logs)
    }

