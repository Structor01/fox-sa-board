import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Configurações gerais
np.random.seed(42)  # Para reprodutibilidade
data_atual = datetime.now()
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Dados simulados realistas para FOX GRÃOS
def gerar_dados_fox_graos():
    """Gera dados simulados para Fox Grãos - Comercialização e Logística de Grãos"""
    
    # Balanço Patrimonial (em milhares de R$)
    balanco_fox_graos = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 15000,
                'Contas a Receber': 45000,
                'Estoques': 85000,  # Alto devido ao estoque de grãos
                'Outros Ativos Circulantes': 8000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 12000,
                'Investimentos': 5000,
                'Imobilizado': 120000,  # Silos, armazéns, equipamentos
                'Intangível': 3000
            }
        },
        'PASSIVO': {
            'Passivo Circulante': {
                'Fornecedores': 35000,  # Pagamentos a produtores
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
    
    # DRE Anual (em milhares de R$)
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
    
    # Dados por commodity (volumes em toneladas, valores em R$/ton)
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

# Dados simulados realistas para FOX LOG
def gerar_dados_fox_log():
    """Gera dados simulados para Fox Log - Transporte de Grãos e Insumos"""
    
    # Balanço Patrimonial (em milhares de R$)
    balanco_fox_log = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 8000,
                'Contas a Receber': 18000,
                'Estoques': 3000,  # Peças e combustível
                'Outros Ativos Circulantes': 2000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 5000,
                'Investimentos': 2000,
                'Imobilizado': 95000,  # Frota de caminhões
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
                'Empréstimos de Longo Prazo': 45000,  # Financiamento da frota
                'Provisões': 2000
            },
            'Patrimônio Líquido': {
                'Capital Social': 40000,
                'Reservas': 8000,
                'Lucros Acumulados': 5000
            }
        }
    }
    
    # DRE Anual (em milhares de R$)
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
        'Depreciação e Amortização': -12000,  # Alta depreciação da frota
        'EBIT': -3000,
        'Resultado Financeiro': -2000,
        'Lucro Antes do IR': -5000,
        'Imposto de Renda e CSLL': 0,
        'Lucro Líquido': -5000
    }
    
    # Dados operacionais da frota
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

# Dados simulados realistas para CLUBE FX
def gerar_dados_clube_fx():
    """Gera dados simulados para Clube FX - Consultoria de Comercialização"""
    
    # Balanço Patrimonial (em milhares de R$)
    balanco_clube_fx = {
        'ATIVO': {
            'Ativo Circulante': {
                'Caixa e Equivalentes': 5000,
                'Contas a Receber': 8000,
                'Estoques': 0,  # Empresa de serviços
                'Outros Ativos Circulantes': 1000
            },
            'Ativo Não Circulante': {
                'Realizável a Longo Prazo': 2000,
                'Investimentos': 3000,
                'Imobilizado': 8000,  # Escritórios e equipamentos
                'Intangível': 5000  # Software e sistemas
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
    
    # DRE Anual (em milhares de R$)
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
    
    # Dados operacionais de consultoria
    operacional_clube_fx = {
        'Clientes': {
            'Total_Clientes_Ativos': 85,
            'Receita_Media_Por_Cliente': 270,  # R$ mil/ano
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

# Gerar dados consolidados
def gerar_dados_consolidados():
    """Gera dados consolidados do Grupo FOX SA"""
    
    # Obter dados individuais
    bal_graos, dre_graos, _ = gerar_dados_fox_graos()
    bal_log, dre_log, _ = gerar_dados_fox_log()
    bal_fx, dre_fx, _ = gerar_dados_clube_fx()
    
    # Consolidar Balanço Patrimonial
    def somar_balanco(item_graos, item_log, item_fx):
        if isinstance(item_graos, dict):
            resultado = {}
            for key in item_graos.keys():
                resultado[key] = somar_balanco(item_graos[key], item_log[key], item_fx[key])
            return resultado
        else:
            return item_graos + item_log + item_fx
    
    balanco_consolidado = somar_balanco(bal_graos, bal_log, bal_fx)
    
    # Consolidar DRE
    dre_consolidado = {
        'Receita Operacional Bruta': 390000,  # 280k + 85k + 25k
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

if __name__ == "__main__":
    # Gerar todos os dados
    print("Gerando dados simulados para FOX SA...")
    
    # Dados individuais
    bal_graos, dre_graos, comm_graos = gerar_dados_fox_graos()
    bal_log, dre_log, op_log = gerar_dados_fox_log()
    bal_fx, dre_fx, op_fx = gerar_dados_clube_fx()
    
    # Dados consolidados
    bal_consolidado, dre_consolidado = gerar_dados_consolidados()
    
    print("Dados gerados com sucesso!")
    print(f"Fox Grãos - Receita Líquida: R$ {dre_graos['Receita Operacional Líquida']:,} mil")
    print(f"Fox Log - Receita Líquida: R$ {dre_log['Receita Operacional Líquida']:,} mil")
    print(f"Clube FX - Receita Líquida: R$ {dre_fx['Receita Operacional Líquida']:,} mil")
    print(f"Consolidado - Receita Líquida: R$ {dre_consolidado['Receita Operacional Líquida']:,} mil")

