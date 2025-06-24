import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Configurações gerais
np.random.seed(42)  # Para reprodutibilidade
data_atual = datetime.now()

class FOXDataGenerator:
    """
    Gerador de dados estruturado seguindo princípios de EDA
    Baseado na metodologia do blog post Streamlit
    """
    
    def __init__(self):
        self.anos = list(range(2019, 2025))
        self.meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                     'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        self.commodities = ['Soja', 'Milho', 'Sorgo']
        self.empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
        
        # Coordenadas de Goiás para o mapa
        self.cidades_goias = {
            'Goiânia': {'lat': -16.6869, 'lon': -49.2648, 'tipo': 'hub'},
            'Rio Verde': {'lat': -17.7944, 'lon': -50.9267, 'tipo': 'produtor'},
            'Jataí': {'lat': -17.8816, 'lon': -51.7142, 'tipo': 'produtor'},
            'Cristalina': {'lat': -16.7677, 'lon': -47.6137, 'tipo': 'produtor'},
            'Luziânia': {'lat': -16.2573, 'lon': -47.9502, 'tipo': 'comprador'},
            'Anápolis': {'lat': -16.3281, 'lon': -48.9531, 'tipo': 'comprador'},
            'Aparecida de Goiânia': {'lat': -16.8173, 'lon': -49.2437, 'tipo': 'comprador'},
            'Catalão': {'lat': -18.1659, 'lon': -47.9469, 'tipo': 'produtor'},
            'Itumbiara': {'lat': -18.4192, 'lon': -49.2150, 'tipo': 'comprador'},
            'Planaltina': {'lat': -15.4528, 'lon': -47.6581, 'tipo': 'produtor'},
            'Formosa': {'lat': -15.5372, 'lon': -47.3342, 'tipo': 'produtor'},
            'Senador Canedo': {'lat': -16.7014, 'lon': -49.0919, 'tipo': 'comprador'},
            'Quirinópolis': {'lat': -18.4481, 'lon': -50.4503, 'tipo': 'produtor'},
            'Mineiros': {'lat': -17.5697, 'lon': -52.5511, 'tipo': 'produtor'},
            'Chapadão do Céu': {'lat': -18.4067, 'lon': -52.6331, 'tipo': 'produtor'}
        }
        
    def gerar_dados_mapa_goias(self):
        """
        Gera dados para o mapa de Goiás com produtores e compradores
        """
        dados_mapa = []
        
        for cidade, info in self.cidades_goias.items():
            # Volume de negócios baseado no tipo
            if info['tipo'] == 'produtor':
                volume_base = np.random.uniform(5000, 25000)  # toneladas/ano
                cor = '#90EE90'  # Verde para produtores
                simbolo = 'triangle-up'
            elif info['tipo'] == 'comprador':
                volume_base = np.random.uniform(2000, 15000)  # toneladas/ano
                cor = '#FFD700'  # Dourado para compradores
                simbolo = 'circle'
            else:  # hub
                volume_base = np.random.uniform(50000, 100000)  # toneladas/ano
                cor = '#C0C0C0'  # Prata para hub
                simbolo = 'diamond'
            
            # LTV baseado no volume e tipo
            if info['tipo'] == 'produtor':
                ltv_base = volume_base * np.random.uniform(180, 250)  # R$/tonelada
            elif info['tipo'] == 'comprador':
                ltv_base = volume_base * np.random.uniform(120, 180)  # R$/tonelada
            else:  # hub
                ltv_base = volume_base * np.random.uniform(80, 120)  # R$/tonelada
            
            dados_mapa.append({
                'cidade': cidade,
                'latitude': info['lat'],
                'longitude': info['lon'],
                'tipo': info['tipo'],
                'volume_anual': round(volume_base, 0),
                'ltv': round(ltv_base, 0),
                'cor': cor,
                'simbolo': simbolo,
                'empresa_responsavel': np.random.choice(self.empresas),
                'commodities_principais': np.random.choice(self.commodities, 
                                                         size=np.random.randint(1, 4), 
                                                         replace=False).tolist()
            })
        
        return pd.DataFrame(dados_mapa)
    
    def gerar_dados_ltv_detalhado(self):
        """
        Gera dados detalhados de LTV por cliente e segmento
        """
        dados_ltv = []
        
        # Gerar clientes fictícios
        nomes_fazendas = [
            'Fazenda São João', 'Agropecuária Boa Vista', 'Fazenda Santa Maria',
            'Cooperativa Central', 'Fazenda Esperança', 'Agro Cerrado',
            'Fazenda Progresso', 'Cooperativa Regional', 'Fazenda Vitória',
            'Agropecuária Moderna', 'Fazenda Prosperidade', 'Grupo Agro Sul',
            'Fazenda Horizonte', 'Cooperativa União', 'Fazenda Sucesso'
        ]
        
        for i, nome in enumerate(nomes_fazendas):
            # Tempo de relacionamento (anos)
            tempo_relacionamento = np.random.uniform(1, 8)
            
            # Receita anual média
            receita_anual = np.random.uniform(500000, 5000000)  # R$
            
            # LTV baseado no tempo e receita
            ltv_total = receita_anual * tempo_relacionamento * np.random.uniform(0.8, 1.2)
            
            # Segmentação por valor
            if ltv_total > 10000000:
                segmento = 'Premium'
                cor_segmento = '#FFD700'
            elif ltv_total > 5000000:
                segmento = 'Gold'
                cor_segmento = '#C0C0C0'
            elif ltv_total > 2000000:
                segmento = 'Silver'
                cor_segmento = '#CD7F32'
            else:
                segmento = 'Bronze'
                cor_segmento = '#8B4513'
            
            dados_ltv.append({
                'cliente': nome,
                'empresa_fox': np.random.choice(self.empresas),
                'tempo_relacionamento': round(tempo_relacionamento, 1),
                'receita_anual': round(receita_anual, 0),
                'ltv_total': round(ltv_total, 0),
                'ltv_mensal': round(ltv_total / (tempo_relacionamento * 12), 0),
                'segmento': segmento,
                'cor_segmento': cor_segmento,
                'cidade': np.random.choice(list(self.cidades_goias.keys())),
                'commodities': np.random.choice(self.commodities, 
                                              size=np.random.randint(1, 3), 
                                              replace=False).tolist(),
                'status': np.random.choice(['Ativo', 'Ativo', 'Ativo', 'Inativo'], p=[0.85, 0.1, 0.04, 0.01])
            })
        
        return pd.DataFrame(dados_ltv)
        
    def gerar_dados_temporais(self):
        """
        Gera dados temporais para análise de tendências
        Similar ao dataset de população do blog post
        """
        dados_temporais = []
        
        for ano in self.anos:
            for mes_idx, mes in enumerate(self.meses):
                # Fox Grãos - Receita mensal com sazonalidade
                receita_base_graos = 22000  # R$ mil/mês
                sazonalidade_graos = 1 + 0.3 * np.sin(2 * np.pi * mes_idx / 12)  # Pico na safra
                crescimento_graos = 1 + 0.08 * (ano - 2019)  # 8% ao ano
                receita_graos = receita_base_graos * sazonalidade_graos * crescimento_graos
                
                # Fox Log - Receita mensal
                receita_base_log = 6600  # R$ mil/mês
                sazonalidade_log = 1 + 0.2 * np.sin(2 * np.pi * mes_idx / 12)
                crescimento_log = 1 + 0.05 * (ano - 2019)  # 5% ao ano
                receita_log = receita_base_log * sazonalidade_log * crescimento_log
                
                # Clube FX - Receita mensal
                receita_base_fx = 1900  # R$ mil/mês
                crescimento_fx = 1 + 0.12 * (ano - 2019)  # 12% ao ano
                receita_fx = receita_base_fx * crescimento_fx
                
                # Adicionar ruído realista
                receita_graos *= (1 + np.random.normal(0, 0.05))
                receita_log *= (1 + np.random.normal(0, 0.08))
                receita_fx *= (1 + np.random.normal(0, 0.06))
                
                dados_temporais.extend([
                    {
                        'empresa': 'Fox Grãos',
                        'ano': ano,
                        'mes': mes,
                        'mes_num': mes_idx + 1,
                        'receita': round(receita_graos, 0),
                        'data': f"{ano}-{mes_idx+1:02d}-01"
                    },
                    {
                        'empresa': 'Fox Log',
                        'ano': ano,
                        'mes': mes,
                        'mes_num': mes_idx + 1,
                        'receita': round(receita_log, 0),
                        'data': f"{ano}-{mes_idx+1:02d}-01"
                    },
                    {
                        'empresa': 'Clube FX',
                        'ano': ano,
                        'mes': mes,
                        'mes_num': mes_idx + 1,
                        'receita': round(receita_fx, 0),
                        'data': f"{ano}-{mes_idx+1:02d}-01"
                    }
                ])
        
        return pd.DataFrame(dados_temporais)
    
    def gerar_dados_commodities_temporais(self):
        """
        Gera dados de commodities ao longo do tempo
        """
        dados_commodities = []
        
        for ano in self.anos:
            for mes_idx, mes in enumerate(self.meses):
                for commodity in self.commodities:
                    # Preços base por commodity
                    precos_base = {'Soja': 4200, 'Milho': 2800, 'Sorgo': 2600}
                    
                    # Tendência de preços
                    tendencia = 1 + 0.06 * (ano - 2019)  # 6% ao ano
                    sazonalidade = 1 + 0.15 * np.sin(2 * np.pi * mes_idx / 12)
                    volatilidade = 1 + np.random.normal(0, 0.12)
                    
                    preco = precos_base[commodity] * tendencia * sazonalidade * volatilidade
                    
                    # Volume comercializado
                    volumes_base = {'Soja': 3800, 'Milho': 2900, 'Sorgo': 670}  # ton/mês
                    volume_sazonalidade = 1 + 0.4 * np.sin(2 * np.pi * (mes_idx + 3) / 12)  # Pico pós-safra
                    volume = volumes_base[commodity] * volume_sazonalidade * (1 + np.random.normal(0, 0.1))
                    
                    dados_commodities.append({
                        'commodity': commodity,
                        'ano': ano,
                        'mes': mes,
                        'mes_num': mes_idx + 1,
                        'preco_medio': round(preco, 2),
                        'volume_comercializado': round(volume, 0),
                        'receita': round(preco * volume / 1000, 0),  # R$ mil
                        'data': f"{ano}-{mes_idx+1:02d}-01"
                    })
        
        return pd.DataFrame(dados_commodities)
    
    def gerar_metricas_performance(self):
        """
        Gera métricas de performance para heatmap
        Similar ao exemplo do blog post
        """
        performance_data = []
        
        for ano in [2023, 2024]:
            for mes_idx, mes in enumerate(self.meses):
                for empresa in self.empresas:
                    # Performance base por empresa
                    performance_base = {
                        'Fox Grãos': 85,
                        'Fox Log': 78,
                        'Clube FX': 92
                    }
                    
                    # Variação sazonal e aleatória
                    sazonalidade = 5 * np.sin(2 * np.pi * mes_idx / 12)
                    ruido = np.random.normal(0, 8)
                    
                    performance = performance_base[empresa] + sazonalidade + ruido
                    performance = max(60, min(100, performance))  # Limitar entre 60-100
                    
                    performance_data.append({
                        'empresa': empresa,
                        'ano': ano,
                        'mes': mes,
                        'mes_num': mes_idx + 1,
                        'performance': round(performance, 1),
                        'data': f"{ano}-{mes_idx+1:02d}-01"
                    })
        
        return pd.DataFrame(performance_data)
    
    def gerar_dados_migracao_estados(self):
        """
        Gera dados de 'migração' de commodities entre regiões
        Adaptação do conceito de migração populacional
        """
        estados = ['MT', 'GO', 'MS', 'PR', 'RS', 'BA', 'MG', 'SP']
        dados_migracao = []
        
        for estado in estados:
            for commodity in self.commodities:
                # Volume base por estado e commodity
                volumes_base = {
                    'MT': {'Soja': 15000, 'Milho': 8000, 'Sorgo': 1200},
                    'GO': {'Soja': 12000, 'Milho': 6500, 'Sorgo': 2000},
                    'MS': {'Soja': 8000, 'Milho': 4500, 'Sorgo': 800},
                    'PR': {'Soja': 10000, 'Milho': 7000, 'Sorgo': 600},
                    'RS': {'Soja': 9000, 'Milho': 3000, 'Sorgo': 400},
                    'BA': {'Soja': 3000, 'Milho': 2000, 'Sorgo': 1500},
                    'MG': {'Soja': 4000, 'Milho': 3500, 'Sorgo': 900},
                    'SP': {'Soja': 2000, 'Milho': 2500, 'Sorgo': 300}
                }
                
                volume = volumes_base[estado][commodity]
                
                # Simular entrada e saída (similar a inbound/outbound migration)
                entrada = volume * np.random.uniform(0.8, 1.2)
                saida = volume * np.random.uniform(0.7, 1.1)
                saldo = entrada - saida
                
                dados_migracao.append({
                    'estado': estado,
                    'commodity': commodity,
                    'volume_entrada': round(entrada, 0),
                    'volume_saida': round(saida, 0),
                    'saldo_liquido': round(saldo, 0),
                    'tipo_fluxo': 'Entrada' if saldo > 0 else 'Saída'
                })
        
        return pd.DataFrame(dados_migracao)

# Funções de compatibilidade com o código existente
def gerar_dados_fox_graos():
    """Mantém compatibilidade com código existente"""
    generator = FOXDataGenerator()
    
    # Balanço Patrimonial (em milhares de R$)
    balanco_fox_graos = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 15000,
                'Contas a Receber': 45000,
                'Estoques': 85000,
                'Outros Ativos Circulantes': 8000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 12000,
                'Investimentos': 5000,
                'Imobilizado': 120000,
                'Intangível': 3000
            }
        },
        'PASSIVO': {
            'Passivo Circulante': {
                'Fornecedores': 35000,
                'Empréstimos e Financiamentos': 25000,
                'Salários e Encargos': 4500,
                'Tributos a Pagar': 6500,
                'Outras Obrigações': 8000
            },
            'Passivo Não Circulante': {
                'Empréstimos de Longo Prazo': 80000,
                'Provisões': 3000
            },
            'Patrimônio Líquido': {
                'Capital Social': 100000,
                'Reservas': 15000,
                'Lucros Acumulados': 16000
            }
        }
    }
    
    dre_fox_graos = {
        'Receita Operacional Bruta': 280000,
        'Deduções da Receita': -18000,
        'Receita Operacional Líquida': 262000,
        'Custo dos Produtos Vendidos': -210000,
        'Lucro Bruto': 52000,
        'Despesas Operacionais': {
            'Despesas Administrativas': -15000,
            'Despesas Comerciais': -8000,
            'Outras Despesas Operacionais': -3000
        },
        'EBITDA': 26000,
        'Depreciação e Amortização': -8000,
        'EBIT': 18000,
        'Resultado Financeiro': -5000,
        'Lucro Antes do IR': 13000,
        'Imposto de Renda e CSLL': -4000,
        'Lucro Líquido': 9000
    }
    
    commodities_fox_graos = {
        'Soja': {
            'Volume_Comercializado_Anual': 45000,
            'Preco_Medio_Compra': 4200,
            'Preco_Medio_Venda': 4350,
            'Margem_Por_Tonelada': 150,
            'Estoque_Atual': 12000,
            'Capacidade_Armazenagem': 20000
        },
        'Milho': {
            'Volume_Comercializado_Anual': 35000,
            'Preco_Medio_Compra': 2800,
            'Preco_Medio_Venda': 2920,
            'Margem_Por_Tonelada': 120,
            'Estoque_Atual': 8000,
            'Capacidade_Armazenagem': 15000
        },
        'Sorgo': {
            'Volume_Comercializado_Anual': 8000,
            'Preco_Medio_Compra': 2600,
            'Preco_Medio_Venda': 2710,
            'Margem_Por_Tonelada': 110,
            'Estoque_Atual': 2000,
            'Capacidade_Armazenagem': 5000
        }
    }
    
    return balanco_fox_graos, dre_fox_graos, commodities_fox_graos

def gerar_dados_fox_log():
    """Mantém compatibilidade com código existente"""
    balanco_fox_log = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 8000,
                'Contas a Receber': 18000,
                'Estoques': 3000,
                'Outros Ativos Circulantes': 2000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 5000,
                'Investimentos': 2000,
                'Imobilizado': 95000,
                'Intangível': 1000
            }
        },
        'PASSIVO': {
            'Passivo Circulante': {
                'Fornecedores': 8000,
                'Empréstimos e Financiamentos': 15000,
                'Salários e Encargos': 6000,
                'Tributos a Pagar': 3000,
                'Outras Obrigações': 4000
            },
            'Passivo Não Circulante': {
                'Empréstimos de Longo Prazo': 45000,
                'Provisões': 2000
            },
            'Patrimônio Líquido': {
                'Capital Social': 40000,
                'Reservas': 8000,
                'Lucros Acumulados': 5000
            }
        }
    }
    
    dre_fox_log = {
        'Receita Operacional Bruta': 85000,
        'Deduções da Receita': -5500,
        'Receita Operacional Líquida': 79500,
        'Custo dos Serviços Prestados': -58000,
        'Lucro Bruto': 21500,
        'Despesas Operacionais': {
            'Despesas Administrativas': -8000,
            'Despesas Comerciais': -3000,
            'Outras Despesas Operacionais': -1500
        },
        'EBITDA': 9000,
        'Depreciação e Amortização': -12000,
        'EBIT': -3000,
        'Resultado Financeiro': -2000,
        'Lucro Antes do IR': -5000,
        'Imposto de Renda e CSLL': 0,
        'Lucro Líquido': -5000
    }
    
    operacional_fox_log = {
        'Frota': {
            'Total_Veiculos': 45,
            'Km_Rodados_Mes': 180000,
            'Taxa_Ocupacao_Frota': 0.78,
            'Consumo_Medio_Litros_Km': 0.35,
            'Custo_Combustivel_Mes': 95000,
            'Custo_Manutencao_Mes': 25000
        },
        'Transporte_Por_Commodity': {
            'Soja': {'Volume_Mensal': 8500, 'Receita_Por_Ton': 85},
            'Milho': {'Volume_Mensal': 6200, 'Receita_Por_Ton': 90},
            'Sorgo': {'Volume_Mensal': 1800, 'Receita_Por_Ton': 88},
            'Insumos': {'Volume_Mensal': 2500, 'Receita_Por_Ton': 120}
        }
    }
    
    return balanco_fox_log, dre_fox_log, operacional_fox_log

def gerar_dados_clube_fx():
    """Mantém compatibilidade com código existente"""
    balanco_clube_fx = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 5000,
                'Contas a Receber': 8000,
                'Estoques': 0,
                'Outros Ativos Circulantes': 1000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 2000,
                'Investimentos': 3000,
                'Imobilizado': 8000,
                'Intangível': 5000
            }
        },
        'PASSIVO': {
            'Passivo Circulante': {
                'Fornecedores': 2000,
                'Empréstimos e Financiamentos': 3000,
                'Salários e Encargos': 4000,
                'Tributos a Pagar': 2500,
                'Outras Obrigações': 1500
            },
            'Passivo Não Circulante': {
                'Empréstimos de Longo Prazo': 5000,
                'Provisões': 1000
            },
            'Patrimônio Líquido': {
                'Capital Social': 10000,
                'Reservas': 3000,
                'Lucros Acumulados': 4000
            }
        }
    }
    
    dre_clube_fx = {
        'Receita Operacional Bruta': 25000,
        'Deduções da Receita': -2000,
        'Receita Operacional Líquida': 23000,
        'Custo dos Serviços Prestados': -8000,
        'Lucro Bruto': 15000,
        'Despesas Operacionais': {
            'Despesas Administrativas': -6000,
            'Despesas Comerciais': -2000,
            'Outras Despesas Operacionais': -1000
        },
        'EBITDA': 6000,
        'Depreciação e Amortização': -1500,
        'EBIT': 4500,
        'Resultado Financeiro': -500,
        'Lucro Antes do IR': 4000,
        'Imposto de Renda e CSLL': -1200,
        'Lucro Líquido': 2800
    }
    
    operacional_clube_fx = {
        'Clientes': {
            'Total_Clientes_Ativos': 85,
            'Receita_Media_Por_Cliente': 270,
            'Taxa_Retencao': 0.82,
            'Horas_Consultoria_Mes': 1200,
            'Valor_Hora_Media': 180
        },
        'Assessoria_Por_Commodity': {
            'Soja': {'Volume_Assessorado_Anual': 125000, 'Comissao_Media': 12},
            'Milho': {'Volume_Assessorado_Anual': 95000, 'Comissao_Media': 15},
            'Sorgo': {'Volume_Assessorado_Anual': 25000, 'Comissao_Media': 14}
        }
    }
    
    return balanco_clube_fx, dre_clube_fx, operacional_clube_fx

def gerar_dados_consolidados():
    """Mantém compatibilidade com código existente"""
    bal_graos, dre_graos, _ = gerar_dados_fox_graos()
    bal_log, dre_log, _ = gerar_dados_fox_log()
    bal_fx, dre_fx, _ = gerar_dados_clube_fx()
    
    def somar_balanco(item_graos, item_log, item_fx):
        if isinstance(item_graos, dict):
            resultado = {}
            for key in item_graos.keys():
                resultado[key] = somar_balanco(item_graos[key], item_log[key], item_fx[key])
            return resultado
        else:
            return item_graos + item_log + item_fx
    
    balanco_consolidado = somar_balanco(bal_graos, bal_log, bal_fx)
    
    dre_consolidado = {
        'Receita Operacional Bruta': 390000,
        'Deduções da Receita': -25500,
        'Receita Operacional Líquida': 364500,
        'Custo dos Produtos/Serviços Vendidos': -276000,
        'Lucro Bruto': 88500,
        'Despesas Operacionais': {
            'Despesas Administrativas': -29000,
            'Despesas Comerciais': -13000,
            'Outras Despesas Operacionais': -5500
        },
        'EBITDA': 41000,
        'Depreciação e Amortização': -21500,
        'EBIT': 19500,
        'Resultado Financeiro': -7500,
        'Lucro Antes do IR': 12000,
        'Imposto de Renda e CSLL': -5200,
        'Lucro Líquido': 6800
    }
    
    return balanco_consolidado, dre_consolidado

# Funções para análise exploratória de dados (EDA)
def obter_dados_para_eda():
    """
    Retorna todos os datasets estruturados para EDA
    """
    generator = FOXDataGenerator()
    
    return {
        'dados_temporais': generator.gerar_dados_temporais(),
        'commodities_temporais': generator.gerar_dados_commodities_temporais(),
        'performance_mensal': generator.gerar_metricas_performance(),
        'migracao_commodities': generator.gerar_dados_migracao_estados(),
        'mapa_goias': generator.gerar_dados_mapa_goias(),
        'ltv_detalhado': generator.gerar_dados_ltv_detalhado()
    }

if __name__ == "__main__":
    print("Gerando dados estruturados para EDA...")
    
    # Gerar dados para análise exploratória
    dados_eda = obter_dados_para_eda()
    
    print("Datasets gerados:")
    for nome, df in dados_eda.items():
        print(f"- {nome}: {df.shape[0]} registros, {df.shape[1]} colunas")
    
    # Exemplo de análise
    print("\nExemplo de análise temporal:")
    df_temporal = dados_eda['dados_temporais']
    receita_2024 = df_temporal[df_temporal['ano'] == 2024].groupby('empresa')['receita'].sum()
    print(receita_2024)
    
    # Exemplo de análise de mapa
    print("\nExemplo de análise geográfica:")
    df_mapa = dados_eda['mapa_goias']
    print(f"Total de pontos no mapa: {len(df_mapa)}")
    print(f"Produtores: {len(df_mapa[df_mapa['tipo'] == 'produtor'])}")
    print(f"Compradores: {len(df_mapa[df_mapa['tipo'] == 'comprador'])}")
    
    # Exemplo de análise LTV
    print("\nExemplo de análise LTV:")
    df_ltv = dados_eda['ltv_detalhado']
    ltv_por_segmento = df_ltv.groupby('segmento')['ltv_total'].agg(['count', 'mean', 'sum'])
    print(ltv_por_segmento)
    
    print("\nDados gerados com sucesso seguindo princípios de EDA!")

