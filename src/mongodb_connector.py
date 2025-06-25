"""
Módulo para conexão e consulta ao MongoDB da FOX SA
Collection: orderv2 (contratos)
"""

import pymongo
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FOXMongoConnector:
    """Conector para MongoDB da FOX SA"""
    
    def __init__(self):
        self.connection_string = "mongodb+srv://doadmin:5vk9a08N2tX3e64U@foxdigital-e8bf0024.mongo.ondigitalocean.com/fox?authSource=admin&replicaSet=foxdigital"
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Estabelece conexão com MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client.fox
            self.collection = self.db.orderv2
            
            # Teste de conexão
            self.client.admin.command('ping')
            logger.info("Conexão com MongoDB estabelecida com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar com MongoDB: {str(e)}")
            return False
    
    def get_contracts_summary(self, limit: int = 1000) -> pd.DataFrame:
        """
        Busca resumo dos contratos da orderv2
        
        Args:
            limit: Limite de registros a buscar
            
        Returns:
            DataFrame com dados dos contratos
        """
        try:
            if self.collection is None:
                if not self.connect():
                    return pd.DataFrame()
            
            # Pipeline de agregação para buscar dados essenciais
            pipeline = [
                {
                    "$match": {
                        "isCanceled": {"$ne": True},  # Não cancelados
                        "closeDate": {"$exists": True}  # Com data de fechamento
                    }
                },
                {
                    "$lookup": {
                        "from": "grains",
                        "localField": "grain",
                        "foreignField": "_id",
                        "as": "grainInfo"
                    }
                },
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "buyer",
                        "foreignField": "_id",
                        "as": "buyerInfo"
                    }
                },
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "seller",
                        "foreignField": "_id",
                        "as": "sellerInfo"
                    }
                },
                {
                    "$project": {
                        "orderId": 1,
                        "closeDate": 1,
                        "deliveryDeadline": 1,
                        "deliveryDeadlineEnd": 1,
                        "amount": 1,
                        "bagPrice": 1,
                        "isBuying": 1,
                        "isDone": 1,
                        "isInProgress": 1,
                        "amountDone": 1,
                        "amountOrdered": 1,
                        "financialRate": 1,
                        "isCif": 1,
                        "isFob": 1,
                        "paymentDaysAfterDelivery": 1,
                        "grainName": {"$arrayElemAt": ["$grainInfo.name", 0]},
                        "buyerName": {"$arrayElemAt": ["$buyerInfo.name", 0]},
                        "sellerName": {"$arrayElemAt": ["$sellerInfo.name", 0]},
                        "createdAt": 1,
                        "updatedAt": 1
                    }
                },
                {
                    "$sort": {"closeDate": -1}
                },
                {
                    "$limit": limit
                }
            ]
            
            # Executar agregação
            cursor = self.collection.aggregate(pipeline)
            contracts = list(cursor)
            
            if not contracts:
                logger.warning("Nenhum contrato encontrado")
                return pd.DataFrame()
            
            # Converter para DataFrame
            df = pd.DataFrame(contracts)
            
            # Processar dados
            df = self._process_contracts_data(df)
            
            logger.info(f"Carregados {len(df)} contratos do MongoDB")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao buscar contratos: {str(e)}")
            return pd.DataFrame()
    
    def _process_contracts_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa e limpa os dados dos contratos"""
        try:
            # Converter datas
            date_columns = ['closeDate', 'deliveryDeadline', 'deliveryDeadlineEnd', 'createdAt', 'updatedAt']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Calcular valor total do contrato
            df['valorTotal'] = df['amount'] * df['bagPrice']
            
            # Calcular dias para entrega
            df['diasParaEntrega'] = (df['deliveryDeadline'] - datetime.now()).dt.days
            
            # Calcular duração da janela de entrega
            df['duracaoJanelaEntrega'] = (df['deliveryDeadlineEnd'] - df['deliveryDeadline']).dt.days
            
            # Status do contrato
            df['status'] = df.apply(self._get_contract_status, axis=1)
            
            # Mês/Ano de fechamento
            df['mesAnoFechamento'] = df['closeDate'].dt.to_period('M')
            
            # Trimestre de fechamento
            df['trimestreFechamento'] = df['closeDate'].dt.to_period('Q')
            
            # Tipo de operação
            df['tipoOperacao'] = df['isBuying'].apply(lambda x: 'Compra' if x else 'Venda')
            
            # Modalidade de frete
            df['modalidadeFrete'] = df.apply(lambda x: 'CIF' if x['isCif'] else 'FOB', axis=1)
            
            # Preencher valores nulos
            df['grainName'] = df['grainName'].fillna('Não informado')
            df['buyerName'] = df['buyerName'].fillna('Não informado')
            df['sellerName'] = df['sellerName'].fillna('Não informado')
            df['financialRate'] = df['financialRate'].fillna(0)
            df['paymentDaysAfterDelivery'] = df['paymentDaysAfterDelivery'].fillna('0')
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao processar dados: {str(e)}")
            return df
    
    def _get_contract_status(self, row) -> str:
        """Determina o status do contrato"""
        if row['isDone']:
            return 'Concluído'
        elif row['isInProgress']:
            return 'Em Andamento'
        elif row['diasParaEntrega'] < 0:
            return 'Vencido'
        elif row['diasParaEntrega'] <= 30:
            return 'Próximo ao Vencimento'
        else:
            return 'Ativo'
    
    def get_financial_summary(self, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> Dict:
        """
        Busca resumo financeiro dos contratos
        
        Args:
            start_date: Data inicial do filtro
            end_date: Data final do filtro
            
        Returns:
            Dicionário com métricas financeiras
        """
        try:
            df = self.get_contracts_summary()
            
            if df.empty:
                return {}
            
            # Filtrar por data se especificado
            if start_date:
                df = df[df['closeDate'] >= start_date]
            if end_date:
                df = df[df['closeDate'] <= end_date]
            
            # Calcular métricas
            summary = {
                'totalContratos': len(df),
                'valorTotalContratos': df['valorTotal'].sum(),
                'valorMedioContrato': df['valorTotal'].mean(),
                'volumeTotalSacas': df['amount'].sum(),
                'precoMedioSaca': df['bagPrice'].mean(),
                'contratosConcluidos': len(df[df['status'] == 'Concluído']),
                'contratosEmAndamento': len(df[df['status'] == 'Em Andamento']),
                'contratosAtivos': len(df[df['status'] == 'Ativo']),
                'contratosVencidos': len(df[df['status'] == 'Vencido']),
                'percentualConclusao': (len(df[df['status'] == 'Concluído']) / len(df) * 100) if len(df) > 0 else 0,
                'graosComercializados': df['grainName'].value_counts().to_dict(),
                'operacoesPorTipo': df['tipoOperacao'].value_counts().to_dict(),
                'modalidadesFrete': df['modalidadeFrete'].value_counts().to_dict()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo financeiro: {str(e)}")
            return {}
    
    def get_monthly_performance(self, year: int = None) -> pd.DataFrame:
        """
        Busca performance mensal dos contratos
        
        Args:
            year: Ano para filtrar (padrão: ano atual)
            
        Returns:
            DataFrame com performance mensal
        """
        try:
            df = self.get_contracts_summary()
            
            if df.empty:
                return pd.DataFrame()
            
            # Filtrar por ano se especificado
            if year:
                df = df[df['closeDate'].dt.year == year]
            
            # Agrupar por mês
            monthly = df.groupby(df['closeDate'].dt.to_period('M')).agg({
                'orderId': 'count',
                'valorTotal': 'sum',
                'amount': 'sum',
                'bagPrice': 'mean'
            }).reset_index()
            
            monthly.columns = ['mes', 'numeroContratos', 'valorTotal', 'volumeTotal', 'precoMedio']
            monthly['mes'] = monthly['mes'].astype(str)
            
            return monthly
            
        except Exception as e:
            logger.error(f"Erro ao buscar performance mensal: {str(e)}")
            return pd.DataFrame()
    
    def close_connection(self):
        """Fecha conexão com MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Conexão com MongoDB fechada")

# Instância global do conector
@st.cache_resource
def get_mongo_connector():
    """Retorna instância cached do conector MongoDB"""
    return FOXMongoConnector()

# Funções utilitárias para uso no Streamlit
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_contracts_data(limit: int = 1000):
    """Carrega dados dos contratos com cache"""
    connector = get_mongo_connector()
    return connector.get_contracts_summary(limit)

@st.cache_data(ttl=300)
def load_financial_summary(start_date=None, end_date=None):
    """Carrega resumo financeiro com cache"""
    connector = get_mongo_connector()
    return connector.get_financial_summary(start_date, end_date)

@st.cache_data(ttl=300)
def load_monthly_performance(year=None):
    """Carrega performance mensal com cache"""
    connector = get_mongo_connector()
    return connector.get_monthly_performance(year)

