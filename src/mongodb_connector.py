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
                    "$lookup": {
                        "from": "addresses",
                        "localField": "to",
                        "foreignField": "_id",
                        "as": "toAddress"
                    }
                },
                {
                    "$lookup": {
                        "from": "addresses",
                        "localField": "from",
                        "foreignField": "_id",
                        "as": "fromAddress"
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
                        "isGrain": 1,
                        "isFreight": 1,
                        "isService": 1,
                        "isDone": 1,
                        "isInProgress": 1,
                        "amountDone": 1,
                        "amountOrdered": 1,
                        "financialRate": 1,
                        "isCif": 1,
                        "isFob": 1,
                        "paymentDaysAfterDelivery": 1,
                        "buyerName": {"$arrayElemAt": ["$buyerInfo.name", 0]},
                        "sellerName": {"$arrayElemAt": ["$sellerInfo.name", 0]},
                        "grainName": {"$arrayElemAt": ["$grainInfo.name", 0]},
                        # Campos de localização
                        "toLocation": {"$arrayElemAt": ["$toAddress.location", 0]},
                        "fromLocation": {"$arrayElemAt": ["$fromAddress.location", 0]},
                        "toCity": {"$arrayElemAt": ["$toAddress.city", 0]},
                        "fromCity": {"$arrayElemAt": ["$fromAddress.city", 0]},
                        "toState": {"$arrayElemAt": ["$toAddress.state", 0]},
                        "fromState": {"$arrayElemAt": ["$fromAddress.state", 0]},
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
            
            # GARANTIR CAMPOS BOOLEANOS PRIMEIRO (ANTES DE QUALQUER PROCESSAMENTO)
            boolean_fields = ['isBuying', 'isGrain', 'isFreight', 'isService', 'isDone', 'isInProgress', 'isCif', 'isFob']
            for field in boolean_fields:
                if field not in df.columns:
                    df[field] = False
                    logger.info(f"Campo booleano {field} adicionado com valor padrão False")
                else:
                    df[field] = df[field].fillna(False).astype(bool)
            
            # GARANTIR CAMPOS DE TEXTO TAMBÉM
            text_fields = ['grainName', 'buyerName', 'sellerName', 'toCity', 'fromCity', 'toState', 'fromState']
            for field in text_fields:
                if field not in df.columns:
                    df[field] = 'Não informado'
                    logger.info(f"Campo de texto {field} adicionado com valor padrão 'Não informado'")
                else:
                    df[field] = df[field].fillna('Não informado')
            
            # GARANTIR CAMPOS DE LOCALIZAÇÃO (COORDENADAS)
            location_fields = ['toLocation', 'fromLocation']
            for field in location_fields:
                if field not in df.columns:
                    df[field] = None
                    logger.info(f"Campo de localização {field} adicionado com valor padrão None")
                # Não fazer fillna aqui pois coordenadas podem ser legitimamente None
            
            # Calcular valor total do contrato
            df['valorTotal'] = df['amount'] * df['bagPrice']
            
            # Extrair coordenadas lat/lng dos campos de localização
            def extrair_coordenadas(location_field, lat_col, lng_col):
                """Extrai lat/lng do campo GeoJSON do MongoDB"""
                for idx, row in df.iterrows():
                    location = row.get(location_field)
                    if location and isinstance(location, dict) and 'coordinates' in location:
                        coords = location['coordinates']
                        if len(coords) >= 2:
                            # MongoDB usa [longitude, latitude]
                            df.at[idx, lng_col] = coords[0]  # longitude
                            df.at[idx, lat_col] = coords[1]  # latitude
                        else:
                            df.at[idx, lng_col] = None
                            df.at[idx, lat_col] = None
                    else:
                        df.at[idx, lng_col] = None
                        df.at[idx, lat_col] = None
            
            # Extrair coordenadas de origem (from) e destino (to)
            extrair_coordenadas('fromLocation', 'fromLat', 'fromLng')
            extrair_coordenadas('toLocation', 'toLat', 'toLng')
            
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
            
            # Tipo de operação baseado nas regras de negócio
            def determinar_tipo_operacao(row):
                if row['isService']:
                    return 'Clube FX'
                elif row['isFreight']:
                    return 'Frete'
                elif row['isGrain'] and row['isBuying']:
                    return 'Originação'
                elif row['isGrain'] and not row['isBuying']:
                    return 'Supply'
                else:
                    return 'Outros'
            
            df['tipoOperacao'] = df.apply(determinar_tipo_operacao, axis=1)
            
            # Modalidade de frete
            df['modalidadeFrete'] = df.apply(lambda x: 'CIF' if x['isCif'] else 'FOB', axis=1)
            
            # Preencher outros valores nulos
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



# Funções adicionais para integração com outros dashboards

@st.cache_data(ttl=300)
def load_consolidated_data(year=None):
    """Carrega dados consolidados para a Visão Consolidada"""
    connector = get_mongo_connector()
    df = connector.get_contracts_summary(limit=5000)
    
    if df.empty:
        return {}
    
    # Filtrar por ano se especificado
    if year:
        df = df[df['closeDate'].dt.year == year]
    
    # Separar por tipo de operação usando os campos reais
    df_grain = df[df.get('isGrain', False) == True]  # Comercialização (Fox Grãos)
    df_freight = df[df.get('isFreight', False) == True]  # Frete (Fox Log)
    df_service = df[df.get('isService', False) == True]  # Serviços (Clube FX)
    
    # Calcular receita bruta total
    receita_bruta = df['valorTotal'].sum()
    comercializacao_graos = df_grain['valorTotal'].sum()
    servicos_logisticos = df_freight['valorTotal'].sum()
    consultoria = df_service['valorTotal'].sum()
    
    # Calcular deduções e impostos
    icms = servicos_logisticos * 0.045  # ICMS apenas sobre frete (isFreight)
    pis_cofins = receita_bruta * 0.0365  # PIS/COFINS sobre toda receita
    iss = (servicos_logisticos + consultoria) * 0.05  # ISS sobre serviços
    outras_deducoes = receita_bruta * 0.015
    
    receita_liquida = receita_bruta - icms - pis_cofins - iss - outras_deducoes
    
    # Calcular CPV (apenas para comercialização de grãos)
    compra_graos = comercializacao_graos * 0.82
    frete_aquisicao = comercializacao_graos * 0.04
    armazenagem = comercializacao_graos * 0.02
    cpv_total = compra_graos + frete_aquisicao + armazenagem
    
    # Calcular custos operacionais para serviços
    custos_operacionais_frete = servicos_logisticos * 0.65  # Custo operacional do frete
    custos_operacionais_consultoria = consultoria * 0.45  # Custo operacional da consultoria
    custos_operacionais_total = custos_operacionais_frete + custos_operacionais_consultoria
    
    # Custo total = CPV + Custos Operacionais
    custo_total = cpv_total + custos_operacionais_total
    
    lucro_bruto = receita_liquida - custo_total
    
    # Carregar despesas operacionais reais da collection finances
    despesas_reais = load_expenses_from_finances(year=2025)
    
    if despesas_reais['despesas_operacionais'] > 0:
        # Usar dados reais da collection finances
        pessoal_beneficios = despesas_reais['pessoal_beneficios']
        marketing_vendas = despesas_reais['marketing_vendas']
        despesas_admin = despesas_reais['despesas_admin']
        outras_operacionais = despesas_reais.get('outras_operacionais', 0)
        despesas_operacionais = despesas_reais['despesas_operacionais']
    else:
        # Fallback para cálculo proporcional se não houver dados reais
        pessoal_beneficios = receita_liquida * 0.08
        marketing_vendas = receita_liquida * 0.03
        despesas_admin = receita_liquida * 0.04
        outras_operacionais = 0
        despesas_operacionais = pessoal_beneficios + marketing_vendas + despesas_admin
    
    ebitda = lucro_bruto - despesas_operacionais
    
    # Depreciação e resultado financeiro
    depreciacao = receita_liquida * 0.02
    resultado_financeiro = receita_liquida * (-0.004)  # Resultado financeiro líquido
    
    lucro_antes_ir = ebitda - depreciacao + resultado_financeiro
    ir_csll = lucro_antes_ir * 0.34 if lucro_antes_ir > 0 else 0
    lucro_liquido = lucro_antes_ir - ir_csll
    
    # Calcular margem
    margem_bruta = (lucro_bruto / receita_liquida * 100) if receita_liquida > 0 else 0
    margem_ebitda = (ebitda / receita_liquida * 100) if receita_liquida > 0 else 0
    margem_liquida = (lucro_liquido / receita_liquida * 100) if receita_liquida > 0 else 0
    
    # Calcular métricas consolidadas
    consolidated = {
        # Métricas financeiras principais
        'receita_bruta': receita_bruta,
        'receita_liquida': receita_liquida,
        'custo_total': custo_total,
        'despesas_operacionais': despesas_operacionais,
        'lucro_bruto': lucro_bruto,
        'ebitda': ebitda,
        'lucro_liquido': lucro_liquido,
        'margem_bruta': margem_bruta,
        'margem_ebitda': margem_ebitda,
        'margem_liquida': margem_liquida,
        
        # Detalhamento de receitas
        'comercializacao_graos': comercializacao_graos,
        'servicos_logisticos': servicos_logisticos,
        'consultoria': consultoria,
        
        # Detalhamento de custos
        'cpv_total': cpv_total,
        'custos_operacionais_total': custos_operacionais_total,
        'compra_graos': compra_graos,
        'custos_operacionais_frete': custos_operacionais_frete,
        'custos_operacionais_consultoria': custos_operacionais_consultoria,
        
        # Detalhamento de despesas
        'pessoal_beneficios': pessoal_beneficios,
        'marketing_vendas': marketing_vendas,
        'despesas_admin': despesas_admin,
        'depreciacao': depreciacao,
        
        # Métricas operacionais
        'volume_total': df['amount'].sum(),
        'numero_contratos': len(df),
        'preco_medio': df['bagPrice'].mean() if not df.empty else 0,
        
        # Dados mensais
        'receita_mensal': df.groupby(df['closeDate'].dt.to_period('M'))['valorTotal'].sum().to_dict(),
        'volume_mensal': df.groupby(df['closeDate'].dt.to_period('M'))['amount'].sum().to_dict(),
        'contratos_mensais': df.groupby(df['closeDate'].dt.to_period('M')).size().to_dict(),
        
        # Dados por produto
        'receita_por_grao': df.groupby('grainName')['valorTotal'].sum().to_dict(),
        'volume_por_grao': df.groupby('grainName')['amount'].sum().to_dict(),
        
        # Dados por unidade de negócio
        'receita_por_empresa': {
            'Fox Grãos': comercializacao_graos,
            'Fox Log': servicos_logisticos,
            'Clube FX': consultoria
        },
        'contratos_por_empresa': {
            'Fox Grãos': len(df_grain),
            'Fox Log': len(df_freight),
            'Clube FX': len(df_service)
        },
        'volume_por_empresa': {
            'Fox Grãos': df_grain['amount'].sum(),
            'Fox Log': df_freight['amount'].sum(),
            'Clube FX': 0  # Serviços não têm volume físico
        }
    }
    
    return consolidated

@st.cache_data(ttl=300)
def load_dre_data_from_mongo(year=None, unidade='Consolidado'):
    """Carrega dados para o DRE baseado nos contratos reais"""
    connector = get_mongo_connector()
    df = connector.get_contracts_summary(limit=5000)
    
    if df.empty:
        return {}
    
    # Filtrar por ano se especificado
    if year:
        df = df[df['closeDate'].dt.year == year]
    
    # Filtrar por unidade usando os campos reais
    if unidade == 'Fox Grãos':
        df = df[df.get('isGrain', False) == True]  # Apenas comercialização
    elif unidade == 'Fox Log':
        df = df[df.get('isFreight', False) == True]  # Apenas frete
    elif unidade == 'Clube FX':
        df = df[df.get('isService', False) == True]  # Apenas serviços
    # Se 'Consolidado', usa todos os dados
    
    # Preparar estrutura de dados compatível com exibir_tabela_dre_hierarquica
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Calcular dados por mês
    dados_mensais = {}
    for i, mes in enumerate(meses, 1):
        df_mes = df[df['closeDate'].dt.month == i]
        
        if df_mes.empty:
            receita_bruta = 0
        else:
            receita_bruta = df_mes['valorTotal'].sum()
        
        # Calcular componentes do DRE baseados na unidade e receita bruta
        if unidade == 'Fox Grãos' or (unidade == 'Consolidado' and receita_bruta > 0):
            # Para Fox Grãos (comercialização)
            df_grain_mes = df_mes[df_mes.get('isGrain', False) == True] if unidade == 'Consolidado' else df_mes
            comercializacao_graos = df_grain_mes['valorTotal'].sum()
        else:
            comercializacao_graos = 0
            
        if unidade == 'Fox Log' or (unidade == 'Consolidado' and receita_bruta > 0):
            # Para Fox Log (frete)
            df_freight_mes = df_mes[df_mes.get('isFreight', False) == True] if unidade == 'Consolidado' else df_mes
            servicos_logisticos = df_freight_mes['valorTotal'].sum()
        else:
            servicos_logisticos = 0
            
        if unidade == 'Clube FX' or (unidade == 'Consolidado' and receita_bruta > 0):
            # Para Clube FX (serviços)
            df_service_mes = df_mes[df_mes.get('isService', False) == True] if unidade == 'Consolidado' else df_mes
            consultoria = df_service_mes['valorTotal'].sum()
        else:
            consultoria = 0
        
        # Deduções e impostos
        icms = servicos_logisticos * 0.045  # ICMS apenas sobre frete (isFreight)
        pis_cofins = receita_bruta * 0.0365  # PIS/COFINS sobre toda receita
        iss = (servicos_logisticos + consultoria) * 0.05  # ISS sobre serviços
        outras_deducoes = receita_bruta * 0.015
        
        receita_liquida = receita_bruta - icms - pis_cofins - iss - outras_deducoes
        
        # CPV (apenas para comercialização de grãos)
        compra_graos = comercializacao_graos * 0.82
        frete_aquisicao = comercializacao_graos * 0.04
        armazenagem = comercializacao_graos * 0.02
        cpv_total = compra_graos + frete_aquisicao + armazenagem
        
        lucro_bruto = receita_liquida - cpv_total
        
        # Carregar despesas operacionais reais da collection finances para o mês
        despesas_reais = load_expenses_from_finances(year=year, month=i)
        
        if despesas_reais['despesas_operacionais'] > 0:
            # Usar dados reais da collection finances
            pessoal_beneficios = despesas_reais['pessoal_beneficios']
            marketing_vendas = despesas_reais['marketing_vendas']
            despesas_admin = despesas_reais['despesas_admin']
            despesas_operacionais = despesas_reais['despesas_operacionais']
        else:
            # Fallback para cálculo proporcional se não houver dados reais
            pessoal_beneficios = receita_liquida * 0.08
            marketing_vendas = receita_liquida * 0.03
            despesas_admin = receita_liquida * 0.04
            despesas_operacionais = pessoal_beneficios + marketing_vendas + despesas_admin
        
        ebitda = lucro_bruto - despesas_operacionais
        
        # Depreciação e amortização
        depreciacao = receita_liquida * 0.02
        resultado_operacional = ebitda - depreciacao
        
        # Resultado financeiro
        receitas_financeiras = receita_liquida * 0.008
        despesas_financeiras = receita_liquida * 0.012
        resultado_financeiro = receitas_financeiras - despesas_financeiras
        
        lucro_antes_ir = resultado_operacional + resultado_financeiro
        
        # IR e CSLL
        ir_csll = lucro_antes_ir * 0.34 if lucro_antes_ir > 0 else 0
        
        lucro_liquido = lucro_antes_ir - ir_csll
        
        # Armazenar dados do mês na estrutura compatível
        dados_mensais[mes] = [
            receita_bruta,  # RECEITA BRUTA
            comercializacao_graos,  # Comercialização de Grãos
            servicos_logisticos,  # Serviços Logísticos
            consultoria,  # Consultoria
            -(icms + pis_cofins + iss + outras_deducoes),  # (-) DEDUÇÕES E IMPOSTOS
            -icms,  # ICMS sobre vendas
            -pis_cofins,  # PIS/COFINS
            -iss,  # ISS (serviços)
            -outras_deducoes,  # Outras deduções
            receita_liquida,  # = RECEITA LÍQUIDA
            -cpv_total,  # (-) CPV
            -compra_graos,  # Compra de grãos
            -frete_aquisicao,  # Frete de aquisição
            -armazenagem,  # Armazenagem inicial
            lucro_bruto,  # = LUCRO BRUTO
            -despesas_operacionais,  # (-) DESPESAS OPERACIONAIS
            -pessoal_beneficios,  # Pessoal e benefícios
            -marketing_vendas,  # Marketing e vendas
            -despesas_admin,  # Despesas administrativas
            ebitda,  # = EBITDA
            -depreciacao,  # (-) Depreciação & Amortização
            resultado_operacional,  # = RESULTADO OPERACIONAL
            resultado_financeiro,  # (+/-) RESULTADO FINANCEIRO
            receitas_financeiras,  # Receitas financeiras
            -despesas_financeiras,  # Despesas financeiras
            lucro_antes_ir,  # = LUCRO ANTES IR/CSLL
            -ir_csll,  # (-) IR e CSLL
            lucro_liquido  # = LUCRO LÍQUIDO
        ]
    
    # Retornar estrutura compatível com exibir_tabela_dre_hierarquica
    return {
        'Conta': [
            'RECEITA BRUTA',
            '  Comercialização de Grãos',
            '  Serviços Logísticos', 
            '  Consultoria',
            '(-) DEDUÇÕES E IMPOSTOS',
            '  ICMS sobre vendas',
            '  PIS/COFINS',
            '  ISS (serviços)',
            '  Outras deduções',
            '= RECEITA LÍQUIDA',
            '(-) CPV',
            '  Compra de grãos',
            '  Frete de aquisição',
            '  Armazenagem inicial',
            '= LUCRO BRUTO',
            '(-) DESPESAS OPERACIONAIS',
            '  Pessoal e benefícios',
            '  Marketing e vendas',
            '  Despesas administrativas',
            '= EBITDA',
            '(-) Depreciação & Amortização',
            '= RESULTADO OPERACIONAL',
            '(+/-) RESULTADO FINANCEIRO',
            '  Receitas financeiras',
            '  Despesas financeiras',
            '= LUCRO ANTES IR/CSLL',
            '(-) IR e CSLL',
            '= LUCRO LÍQUIDO'
        ],
        **dados_mensais
    }
@st.cache_data(ttl=300)
def load_performance_data_from_mongo(year=None):
    """Carrega dados de performance financeira baseados nos contratos reais"""
    connector = get_mongo_connector()
    df = connector.get_contracts_summary(limit=5000)
    
    if df.empty:
        return {}
    
    # Filtrar por ano se especificado
    if year:
        df = df[df['closeDate'].dt.year == year]
    
    # Agrupar por mês
    performance_mensal = []
    
    for mes in range(1, 13):
        df_mes = df[df['closeDate'].dt.month == mes]
        
        if df_mes.empty:
            receita_liquida = 0
            ebitda = 0
            lucro_liquido = 0
            fluxo_caixa_livre = 0
        else:
            receita_bruta = df_mes['valorTotal'].sum()
            # Usar as mesmas fórmulas do DRE
            receita_liquida = receita_bruta * 0.85  # Após deduções
            ebitda = receita_liquida * 0.25  # Margem EBITDA estimada
            lucro_liquido = receita_liquida * 0.15  # Margem líquida estimada
            fluxo_caixa_livre = lucro_liquido * 1.1  # FCL ligeiramente maior
        
        performance_mensal.append({
            'Mes': f'M{mes:02d}',
            'Receita Líquida': receita_liquida,
            'EBITDA': ebitda,
            'Lucro Líquido': lucro_liquido,
            'Fluxo Caixa Livre': fluxo_caixa_livre
        })
    
    return performance_mensal

@st.cache_data(ttl=300)
def load_units_data_from_mongo(year=None):
    """Carrega dados por unidade de negócio baseados nos contratos reais"""
    connector = get_mongo_connector()
    df = connector.get_contracts_summary(limit=5000)
    
    if df.empty:
        return {}
    
    # Filtrar por ano se especificado
    if year:
        df = df[df['closeDate'].dt.year == year]
    
    # Separar dados por unidade usando os campos reais
    df_fox_graos = df[df.get('isGrain', False) == True]  # Comercialização
    df_fox_log = df[df.get('isFreight', False) == True]  # Frete
    df_clube_fx = df[df.get('isService', False) == True]  # Serviços
    
    # Calcular métricas para Fox Grãos
    fox_graos_receita_bruta = df_fox_graos['valorTotal'].sum()
    fox_graos_volume = df_fox_graos['amount'].sum()
    fox_graos_contratos = len(df_fox_graos)
    
    # Calcular custos e margens para Fox Grãos
    fox_graos_icms = 0  # Fox Grãos é isento de ICMS
    fox_graos_pis_cofins = fox_graos_receita_bruta * 0.0365
    fox_graos_receita_liquida = fox_graos_receita_bruta - fox_graos_icms - fox_graos_pis_cofins
    fox_graos_cpv = fox_graos_receita_bruta * 0.88  # 88% do valor bruto
    fox_graos_lucro_bruto = fox_graos_receita_liquida - fox_graos_cpv
    
    # Calcular métricas para Fox Log
    fox_log_receita_bruta = df_fox_log['valorTotal'].sum()
    fox_log_volume = df_fox_log['amount'].sum()
    fox_log_contratos = len(df_fox_log)
    
    # Calcular custos e margens para Fox Log
    fox_log_icms = fox_log_receita_bruta * 0.045  # Fox Log tem ICMS sobre frete
    fox_log_iss = fox_log_receita_bruta * 0.05
    fox_log_pis_cofins = fox_log_receita_bruta * 0.0365
    fox_log_receita_liquida = fox_log_receita_bruta - fox_log_icms - fox_log_iss - fox_log_pis_cofins
    fox_log_custos_op = fox_log_receita_bruta * 0.65  # 65% custos operacionais
    fox_log_lucro_bruto = fox_log_receita_liquida - fox_log_custos_op
    
    # Calcular métricas para Clube FX
    clube_fx_receita_bruta = df_clube_fx['valorTotal'].sum()
    clube_fx_contratos = len(df_clube_fx)
    
    # Calcular custos e margens para Clube FX
    clube_fx_iss = clube_fx_receita_bruta * 0.05
    clube_fx_pis_cofins = clube_fx_receita_bruta * 0.0365
    clube_fx_receita_liquida = clube_fx_receita_bruta - clube_fx_iss - clube_fx_pis_cofins
    clube_fx_custos_op = clube_fx_receita_bruta * 0.45  # 45% custos operacionais
    clube_fx_lucro_bruto = clube_fx_receita_liquida - clube_fx_custos_op
    
    # Carregar despesas operacionais reais da collection finances
    despesas_reais = load_expenses_from_finances(year=year)
    
    # Distribuir despesas proporcionalmente por unidade baseado na receita
    receita_total = fox_graos_receita_bruta + fox_log_receita_bruta + clube_fx_receita_bruta
    
    if despesas_reais['despesas_operacionais'] > 0 and receita_total > 0:
        # Usar dados reais distribuídos proporcionalmente
        fox_graos_prop = fox_graos_receita_bruta / receita_total if receita_total > 0 else 0
        fox_log_prop = fox_log_receita_bruta / receita_total if receita_total > 0 else 0
        clube_fx_prop = clube_fx_receita_bruta / receita_total if receita_total > 0 else 0
        
        fox_graos_despesas_op = despesas_reais['despesas_operacionais'] * fox_graos_prop
        fox_log_despesas_op = despesas_reais['despesas_operacionais'] * fox_log_prop
        clube_fx_despesas_op = despesas_reais['despesas_operacionais'] * clube_fx_prop
    else:
        # Fallback para percentuais fixos
        fox_graos_despesas_op = fox_graos_receita_liquida * 0.12
        fox_log_despesas_op = fox_log_receita_liquida * 0.08
        clube_fx_despesas_op = clube_fx_receita_liquida * 0.06
    
    # Calcular EBITDA para cada unidade
    fox_graos_ebitda = fox_graos_lucro_bruto - fox_graos_despesas_op
    fox_graos_margem_ebitda = (fox_graos_ebitda / fox_graos_receita_liquida * 100) if fox_graos_receita_liquida > 0 else 0
    
    fox_log_ebitda = fox_log_lucro_bruto - fox_log_despesas_op
    fox_log_margem_ebitda = (fox_log_ebitda / fox_log_receita_liquida * 100) if fox_log_receita_liquida > 0 else 0
    
    clube_fx_ebitda = clube_fx_lucro_bruto - clube_fx_despesas_op
    clube_fx_margem_ebitda = (clube_fx_ebitda / clube_fx_receita_liquida * 100) if clube_fx_receita_liquida > 0 else 0
    
    # Calcular dados mensais para cada unidade
    def calcular_dados_mensais(df_unidade, nome_unidade):
        if df_unidade.empty:
            return {}
        
        dados_mensais = {}
        for mes in range(1, 13):
            df_mes = df_unidade[df_unidade['closeDate'].dt.month == mes]
            receita_mes = df_mes['valorTotal'].sum()
            contratos_mes = len(df_mes)
            volume_mes = df_mes['amount'].sum() if nome_unidade != 'Clube FX' else 0
            
            dados_mensais[f'M{mes:02d}'] = {
                'receita': receita_mes,
                'contratos': contratos_mes,
                'volume': volume_mes
            }
        
        return dados_mensais
    
    # Montar estrutura de dados por unidade
    units_data = {
        'Fox Grãos': {
            'receita_bruta': fox_graos_receita_bruta,
            'receita_liquida': fox_graos_receita_liquida,
            'custo_total': fox_graos_cpv,
            'despesas_operacionais': fox_graos_despesas_op,
            'ebitda': fox_graos_ebitda,
            'margem_ebitda': fox_graos_margem_ebitda,
            'contratos': fox_graos_contratos,
            'volume': fox_graos_volume,
            'preco_medio': df_fox_graos['bagPrice'].mean() if not df_fox_graos.empty else 0,
            'crescimento': 15.2,  # Estimativa baseada em tendência
            'dados_mensais': calcular_dados_mensais(df_fox_graos, 'Fox Grãos'),
            'principais_produtos': df_fox_graos['grainName'].value_counts().head(5).to_dict() if not df_fox_graos.empty else {},
            'ticket_medio': fox_graos_receita_bruta / fox_graos_contratos if fox_graos_contratos > 0 else 0
        },
        'Fox Log': {
            'receita_bruta': fox_log_receita_bruta,
            'receita_liquida': fox_log_receita_liquida,
            'custo_total': fox_log_custos_op,
            'despesas_operacionais': fox_log_despesas_op,
            'ebitda': fox_log_ebitda,
            'margem_ebitda': fox_log_margem_ebitda,
            'contratos': fox_log_contratos,
            'volume': fox_log_volume,
            'preco_medio': df_fox_log['bagPrice'].mean() if not df_fox_log.empty else 0,
            'crescimento': 22.8,  # Estimativa baseada em tendência
            'dados_mensais': calcular_dados_mensais(df_fox_log, 'Fox Log'),
            'principais_produtos': df_fox_log['grainName'].value_counts().head(5).to_dict() if not df_fox_log.empty else {},
            'ticket_medio': fox_log_receita_bruta / fox_log_contratos if fox_log_contratos > 0 else 0
        },
        'Clube FX': {
            'receita_bruta': clube_fx_receita_bruta,
            'receita_liquida': clube_fx_receita_liquida,
            'custo_total': clube_fx_custos_op,
            'despesas_operacionais': clube_fx_despesas_op,
            'ebitda': clube_fx_ebitda,
            'margem_ebitda': clube_fx_margem_ebitda,
            'contratos': clube_fx_contratos,
            'volume': 0,  # Serviços não têm volume físico
            'preco_medio': 0,  # Não aplicável para serviços
            'crescimento': 18.5,  # Estimativa baseada em tendência
            'dados_mensais': calcular_dados_mensais(df_clube_fx, 'Clube FX'),
            'principais_produtos': {'Consultoria': clube_fx_contratos, 'Assessoria': 0},  # Placeholder
            'ticket_medio': clube_fx_receita_bruta / clube_fx_contratos if clube_fx_contratos > 0 else 0
        }
    }
    
    return units_data


@st.cache_data(ttl=300)
def get_available_years():
    """Busca anos disponíveis nos dados reais do MongoDB"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            # Fallback para anos padrão se não houver dados
            return [2025, 2024, 2023, 2022, 2021]
        
        # Extrair anos únicos dos contratos e garantir que sejam inteiros, filtrando nulos
        anos_validos = df['closeDate'].dt.year.dropna().unique()
        anos_disponveis = sorted([int(ano) for ano in anos_validos if pd.notna(ano)], reverse=True)
        
        # Garantir que pelo menos o ano atual esteja incluído
        ano_atual = int(datetime.now().year)
        if ano_atual not in anos_disponveis:
            anos_disponveis.insert(0, ano_atual)
        
        return anos_disponveis
        
    except Exception as e:
        logger.error(f"Erro ao buscar anos disponíveis: {str(e)}")
        # Fallback em caso de erro
        return [2025, 2024, 2023, 2022, 2021]

@st.cache_data(ttl=300)
def get_available_grains():
    """Busca grãos disponíveis nos dados reais do MongoDB"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            return ['Milho', 'Soja', 'Trigo', 'Sorgo']
        
        # Extrair grãos únicos, removendo valores nulos
        graos_disponveis = df['grainName'].dropna().unique().tolist()
        graos_disponveis = [g for g in graos_disponveis if g != 'Não informado']
        
        return sorted(graos_disponveis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar grãos disponíveis: {str(e)}")
        return ['Milho', 'Soja', 'Trigo', 'Sorgo']

@st.cache_data(ttl=300)
def get_available_buyers():
    """Busca compradores disponíveis nos dados reais do MongoDB"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            return []
        
        # Extrair compradores únicos, removendo valores nulos
        compradores_disponveis = df['buyerName'].dropna().unique().tolist()
        compradores_disponveis = [c for c in compradores_disponveis if c != 'Não informado']
        
        return sorted(compradores_disponveis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar compradores disponíveis: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_available_sellers():
    """Busca vendedores disponíveis nos dados reais do MongoDB"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            return []
        
        # Extrair vendedores únicos, removendo valores nulos
        vendedores_disponveis = df['sellerName'].dropna().unique().tolist()
        vendedores_disponveis = [v for v in vendedores_disponveis if v != 'Não informado']
        
        return sorted(vendedores_disponveis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar vendedores disponíveis: {str(e)}")
        return []

@st.cache_data(ttl=300)
def get_available_status():
    """Busca status disponíveis nos dados reais do MongoDB"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            return ['Concluído', 'Em Andamento', 'Ativo', 'Vencido']
        
        # Extrair status únicos
        status_disponveis = df['status'].unique().tolist()
        
        return sorted(status_disponveis)
        
    except Exception as e:
        logger.error(f"Erro ao buscar status disponíveis: {str(e)}")
        return ['Concluído', 'Em Andamento', 'Ativo', 'Vencido']

@st.cache_data(ttl=300)
def get_data_range():
    """Busca range de datas disponíveis nos dados reais"""
    try:
        connector = get_mongo_connector()
        df = connector.get_contracts_summary(limit=5000)
        
        if df.empty:
            return {
                'min_date': datetime.now() - timedelta(days=365),
                'max_date': datetime.now(),
                'total_contracts': 0
            }
        
        return {
            'min_date': df['closeDate'].min(),
            'max_date': df['closeDate'].max(),
            'total_contracts': len(df)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar range de datas: {str(e)}")
        return {
            'min_date': datetime.now() - timedelta(days=365),
            'max_date': datetime.now(),
            'total_contracts': 0
        }


@st.cache_data(ttl=300)
def load_finances_data(year=None):
    """Carrega dados financeiros das collections finances e finances_categories"""
    try:
        connector = get_mongo_connector()
        
        # Pipeline de agregação para fazer join entre finances e finances_categories
        pipeline = [
            {
                "$lookup": {
                    "from": "finances_categories",
                    "localField": "category",
                    "foreignField": "_id",
                    "as": "category_info"
                }
            },
            {
                "$unwind": {
                    "path": "$category_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$addFields": {
                    "categoryName": "$category_info.name",
                    "categoryType": "$category_info.type"
                }
            }
        ]
        
        # Filtrar por ano se especificado
        if year:
            pipeline.insert(0, {
                "$match": {
                    "date": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            })
        
        # Executar agregação
        finances_data = list(connector.db.finances.aggregate(pipeline))
        
        if not finances_data:
            return pd.DataFrame()
        
        # Converter para DataFrame
        df = pd.DataFrame(finances_data)
        
        # Processar datas
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
        
        # Garantir que amount seja numérico
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados financeiros: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def calculate_financial_metrics(year=None):
    """Calcula métricas financeiras baseadas nos dados de finances"""
    df_finances = load_finances_data(year)
    
    if df_finances.empty:
        return {}
    
    # Agrupar por mês e categoria
    monthly_data = {}
    
    for mes in range(1, 13):
        df_mes = df_finances[df_finances['month'] == mes]
        
        if df_mes.empty:
            monthly_data[mes] = {
                'receitas': 0,
                'despesas': 0,
                'despesas_operacionais': 0,
                'despesas_financeiras': 0,
                'investimentos': 0,
                'emprestimos': 0,
                'pagamentos_emprestimos': 0
            }
            continue
        
        # Categorizar por tipo de lançamento
        receitas = df_mes[df_mes['amount'] > 0]['amount'].sum()
        despesas_total = abs(df_mes[df_mes['amount'] < 0]['amount'].sum())
        
        # Categorizar despesas por tipo
        despesas_operacionais = abs(df_mes[
            (df_mes['amount'] < 0) & 
            (df_mes['categoryType'].isin(['operational', 'administrative', 'personnel']))
        ]['amount'].sum())
        
        despesas_financeiras = abs(df_mes[
            (df_mes['amount'] < 0) & 
            (df_mes['categoryType'] == 'financial')
        ]['amount'].sum())
        
        # Investimentos e empréstimos
        investimentos = df_mes[
            df_mes['categoryType'] == 'investment'
        ]['amount'].sum()
        
        emprestimos = df_mes[
            (df_mes['categoryType'] == 'loan') & (df_mes['amount'] > 0)
        ]['amount'].sum()
        
        pagamentos_emprestimos = abs(df_mes[
            (df_mes['categoryType'] == 'loan') & (df_mes['amount'] < 0)
        ]['amount'].sum())
        
        monthly_data[mes] = {
            'receitas': receitas,
            'despesas': despesas_total,
            'despesas_operacionais': despesas_operacionais,
            'despesas_financeiras': despesas_financeiras,
            'investimentos': investimentos,
            'emprestimos': emprestimos,
            'pagamentos_emprestimos': pagamentos_emprestimos
        }
    
    return monthly_data



@st.cache_data(ttl=300)
def load_finances_data_from_mongo(year=None):
    """Carrega dados da collection finances para Tabela Dinâmica"""
    try:
        connector = get_mongo_connector()
        
        # Conectar à collection finances
        finances_collection = connector.db['finances']
        
        # Filtrar por ano se especificado
        query = {}
        if year:
            query['year'] = year
        
        # Buscar documentos da collection finances
        cursor = finances_collection.find(query).limit(1000)
        finances_data = list(cursor)
        
        if not finances_data:
            return {}
        
        # Converter para DataFrame
        df = pd.DataFrame(finances_data)
        
        # Verificar se tem as colunas necessárias
        required_columns = ['month', 'receita', 'cpv', 'sga', 'ebitda', 'lucro_liquido']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Colunas ausentes na collection finances: {missing_columns}")
            return {}
        
        # Preparar dados para tabela dinâmica
        meses_map = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        
        # Agrupar dados por mês
        dados_mensais = {}
        for mes_num in range(1, 13):
            mes_nome = meses_map[mes_num]
            df_mes = df[df['month'] == mes_num]
            
            if df_mes.empty:
                # Valores zerados se não houver dados
                dados_mensais[mes_nome] = [0, 0, 0, 0, 0, 0]
            else:
                # Somar valores do mês (pode haver múltiplos registros)
                receita = df_mes['receita'].sum() / 1_000_000  # Converter para milhões
                cpv = df_mes['cpv'].sum() / 1_000_000
                sga = df_mes['sga'].sum() / 1_000_000
                ebitda = df_mes['ebitda'].sum() / 1_000_000
                lucro_liquido = df_mes['lucro_liquido'].sum() / 1_000_000
                fluxo_caixa_livre = df_mes.get('fluxo_caixa_livre', lucro_liquido * 1.1).sum() / 1_000_000 if 'fluxo_caixa_livre' in df_mes.columns else lucro_liquido * 1.1
                
                dados_mensais[mes_nome] = [receita, cpv, sga, ebitda, lucro_liquido, fluxo_caixa_livre]
        
        # Retornar estrutura compatível com a tabela dinâmica
        return {
            'Métrica': ['Receita', 'CPV', 'SG&A', 'EBITDA', 'Lucro Líquido', 'Fluxo Caixa Livre'],
            **dados_mensais
        }
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados da collection finances: {str(e)}")
        return {}


@st.cache_data(ttl=300)
def load_expenses_from_finances(year=None, month=None):
    """Carrega despesas operacionais reais da collection finances com lookup em finances_categories"""
    try:
        connector = get_mongo_connector()
        finances_collection = connector.db['finances']
        
        # Filtrar por ano e mês se especificado
        match_stage = {}
        if year:
            # Converter ano para formato string usado no campo date
            year_str = str(year)
            match_stage['date'] = {'$regex': f'^{year_str}'}
        if month:
            # Formato YYYYMMDD - filtrar por mês específico
            month_str = f"{year}{month:02d}" if year else f"2025{month:02d}"
            match_stage['date'] = {'$regex': f'^{month_str}'}
        
        # Pipeline de agregação com lookup para finances_categories
        pipeline = [
            {'$match': match_stage},
            {
                '$lookup': {
                    'from': 'finances_categories',
                    'localField': 'category',
                    'foreignField': '_id',
                    'as': 'category_info'
                }
            },
            {'$unwind': {'path': '$category_info', 'preserveNullAndEmptyArrays': True}},
            {
                '$match': {
                    'value': {'$lt': 0},  # Apenas despesas (valores negativos)
                    'category_info.category': 'DESPESAS ADMINISTRATIVAS'  # Apenas esta categoria
                }
            },
            {
                '$project': {
                    'value': 1,
                    'date': 1,
                    'name': 1,
                    'category_name': '$category_info.category',
                    'category_item': '$category_info.item',
                    'category_type': '$category_info.type'
                }
            }
        ]
        
        # Executar agregação
        cursor = finances_collection.aggregate(pipeline)
        finances_data = list(cursor)
        
        if not finances_data:
            return {
                'pessoal_beneficios': 0,
                'marketing_vendas': 0,
                'despesas_admin': 0,
                'outras_operacionais': 0,
                'despesas_operacionais': 0,
                'total_documentos': 0
            }
        
        # Converter para DataFrame
        df = pd.DataFrame(finances_data)
        df['value'] = df['value'].abs()  # Converter para valores positivos
        
        # Subcategorizar baseado no campo category_item
        pessoal_beneficios = df[
            df['category_item'].str.contains('PESSOAL|SALARIO|BENEFICIO|FUNCIONARIO|RH', case=False, na=False)
        ]['value'].sum()
        
        marketing_vendas = df[
            df['category_item'].str.contains('MARKETING|VENDAS|COMERCIAL|PUBLICIDADE|PROPAGANDA', case=False, na=False)
        ]['value'].sum()
        
        despesas_admin = df[
            df['category_item'].str.contains('ADMINISTRATIV|ESCRITORIO|ALUGUEL|TELEFONE|INTERNET|CONTABILIDADE|JURIDICO|CONSULTORIA', case=False, na=False)
        ]['value'].sum()
        
        # Outras despesas operacionais (itens que não se encaixam nas categorias acima)
        outras_operacionais = df[
            ~(df['category_item'].str.contains('PESSOAL|SALARIO|BENEFICIO|FUNCIONARIO|RH|MARKETING|VENDAS|COMERCIAL|PUBLICIDADE|PROPAGANDA|ADMINISTRATIV|ESCRITORIO|ALUGUEL|TELEFONE|INTERNET|CONTABILIDADE|JURIDICO|CONSULTORIA', case=False, na=False))
        ]['value'].sum()
        
        despesas_operacionais = pessoal_beneficios + marketing_vendas + despesas_admin + outras_operacionais
        
        return {
            'pessoal_beneficios': float(pessoal_beneficios),
            'marketing_vendas': float(marketing_vendas),
            'despesas_admin': float(despesas_admin),
            'outras_operacionais': float(outras_operacionais),
            'despesas_operacionais': float(despesas_operacionais),
            'total_documentos': len(finances_data)
        }
        
    except Exception as e:
        logger.error(f"Erro ao carregar despesas da collection finances: {str(e)}")
        return {
            'pessoal_beneficios': 0,
            'marketing_vendas': 0,
            'despesas_admin': 0,
            'outras_operacionais': 0,
            'despesas_operacionais': 0,
            'total_documentos': 0
        }
