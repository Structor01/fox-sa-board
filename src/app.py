import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Importar dados simulados
from gerar_dados_fox import (
    gerar_dados_fox_graos, 
    gerar_dados_fox_log, 
    gerar_dados_clube_fx,
    gerar_dados_consolidados
)

# Configuração da página
st.set_page_config(
    page_title="FOX SA - Board de Gestão",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .company-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E6B3F;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .commodity-tag {
        background-color: #2E8B57;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        margin: 0.1rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Função para formatar valores monetários
def formatar_valor(valor, sufixo="mil"):
    if valor >= 0:
        return f"R$ {valor:,.0f} {sufixo}"
    else:
        return f"-R$ {abs(valor):,.0f} {sufixo}"

# Função para calcular indicadores
def calcular_indicadores(balanco, dre):
    ativo_total = sum([
        sum(balanco['ATIVO']['Ativo Circulante'].values()),
        sum(balanco['ATIVO']['Ativo Não Circulante'].values())
    ])
    
    passivo_circulante = sum(balanco['PASSIVO']['Passivo Circulante'].values())
    passivo_nao_circulante = sum(balanco['PASSIVO']['Passivo Não Circulante'].values())
    patrimonio_liquido = sum(balanco['PASSIVO']['Patrimônio Líquido'].values())
    ativo_circulante = sum(balanco['ATIVO']['Ativo Circulante'].values())
    
    receita_liquida = dre['Receita Operacional Líquida']
    lucro_bruto = dre['Lucro Bruto']
    ebitda = dre['EBITDA']
    lucro_liquido = dre['Lucro Líquido']
    
    indicadores = {
        'Liquidez Corrente': ativo_circulante / passivo_circulante if passivo_circulante > 0 else 0,
        'Endividamento Total': (passivo_circulante + passivo_nao_circulante) / ativo_total if ativo_total > 0 else 0,
        'Margem Bruta (%)': (lucro_bruto / receita_liquida * 100) if receita_liquida > 0 else 0,
        'Margem EBITDA (%)': (ebitda / receita_liquida * 100) if receita_liquida > 0 else 0,
        'Margem Líquida (%)': (lucro_liquido / receita_liquida * 100) if receita_liquida > 0 else 0,
        'ROE (%)': (lucro_liquido / patrimonio_liquido * 100) if patrimonio_liquido > 0 else 0,
        'ROA (%)': (lucro_liquido / ativo_total * 100) if ativo_total > 0 else 0
    }
    
    return indicadores

# Função para criar gráfico de barras comparativo
def criar_grafico_receitas():
    empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
    receitas = [262000, 79500, 23000]
    
    fig = px.bar(
        x=empresas, 
        y=receitas,
        title="Receita Líquida por Empresa (R$ mil)",
        color=empresas,
        color_discrete_sequence=['#2E8B57', '#228B22', '#32CD32']
    )
    fig.update_layout(showlegend=False, height=400)
    return fig

# Função para criar gráfico de commodities
def criar_grafico_commodities():
    commodities = ['Soja', 'Milho', 'Sorgo']
    volumes = [45000, 35000, 8000]
    
    fig = px.pie(
        values=volumes,
        names=commodities,
        title="Volume Comercializado por Commodity (toneladas/ano)",
        color_discrete_sequence=['#8B4513', '#FFD700', '#CD853F']
    )
    return fig

# Função para exibir balanço patrimonial
def exibir_balanco(balanco, empresa):
    st.markdown(f"### 📊 Balanço Patrimonial - {empresa}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ATIVO")
        st.markdown("**Ativo Circulante**")
        for item, valor in balanco['ATIVO']['Ativo Circulante'].items():
            st.write(f"• {item}: {formatar_valor(valor)}")
        
        st.markdown("**Ativo Não Circulante**")
        for item, valor in balanco['ATIVO']['Ativo Não Circulante'].items():
            st.write(f"• {item}: {formatar_valor(valor)}")
        
        ativo_total = sum([
            sum(balanco['ATIVO']['Ativo Circulante'].values()),
            sum(balanco['ATIVO']['Ativo Não Circulante'].values())
        ])
        st.markdown(f"**TOTAL DO ATIVO: {formatar_valor(ativo_total)}**")
    
    with col2:
        st.markdown("#### PASSIVO")
        st.markdown("**Passivo Circulante**")
        for item, valor in balanco['PASSIVO']['Passivo Circulante'].items():
            st.write(f"• {item}: {formatar_valor(valor)}")
        
        st.markdown("**Passivo Não Circulante**")
        for item, valor in balanco['PASSIVO']['Passivo Não Circulante'].items():
            st.write(f"• {item}: {formatar_valor(valor)}")
        
        st.markdown("**Patrimônio Líquido**")
        for item, valor in balanco['PASSIVO']['Patrimônio Líquido'].items():
            st.write(f"• {item}: {formatar_valor(valor)}")
        
        passivo_total = sum([
            sum(balanco['PASSIVO']['Passivo Circulante'].values()),
            sum(balanco['PASSIVO']['Passivo Não Circulante'].values()),
            sum(balanco['PASSIVO']['Patrimônio Líquido'].values())
        ])
        st.markdown(f"**TOTAL DO PASSIVO: {formatar_valor(passivo_total)}**")

# Função para exibir DRE
def exibir_dre(dre, empresa):
    st.markdown(f"### 📈 Demonstração do Resultado - {empresa}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Receita Operacional Bruta:** {formatar_valor(dre['Receita Operacional Bruta'])}")
        st.write(f"**(-) Deduções da Receita:** {formatar_valor(dre['Deduções da Receita'])}")
        st.write(f"**= Receita Operacional Líquida:** {formatar_valor(dre['Receita Operacional Líquida'])}")
        
        custo_key = 'Custo dos Produtos Vendidos' if 'Custo dos Produtos Vendidos' in dre else 'Custo dos Serviços Prestados'
        st.write(f"**(-) {custo_key}:** {formatar_valor(dre.get(custo_key, dre.get('Custo dos Produtos/Serviços Vendidos', 0)))}")
        st.write(f"**= Lucro Bruto:** {formatar_valor(dre['Lucro Bruto'])}")
        
        st.write("**(-) Despesas Operacionais:**")
        for desp, valor in dre['Despesas Operacionais'].items():
            st.write(f"    • {desp}: {formatar_valor(valor)}")
        
        st.write(f"**= EBITDA:** {formatar_valor(dre['EBITDA'])}")
        st.write(f"**(-) Depreciação e Amortização:** {formatar_valor(dre['Depreciação e Amortização'])}")
        st.write(f"**= EBIT:** {formatar_valor(dre['EBIT'])}")
        st.write(f"**(+/-) Resultado Financeiro:** {formatar_valor(dre['Resultado Financeiro'])}")
        st.write(f"**= Lucro Antes do IR:** {formatar_valor(dre['Lucro Antes do IR'])}")
        st.write(f"**(-) Imposto de Renda e CSLL:** {formatar_valor(dre['Imposto de Renda e CSLL'])}")
        st.write(f"**= LUCRO LÍQUIDO:** {formatar_valor(dre['Lucro Líquido'])}")

# Função principal
def main():
    # Título principal
    st.markdown('<h1 class="main-header">🌾 FOX SA - Board de Gestão</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Navegação")
    opcao = st.sidebar.selectbox(
        "Selecione a visualização:",
        ["🏠 Visão Consolidada", "🌾 Fox Grãos", "🚛 Fox Log", "💼 Clube FX", "📊 Análise por Commodity", "📈 Indicadores Comparativos"]
    )
    
    # Carregar dados
    bal_graos, dre_graos, comm_graos = gerar_dados_fox_graos()
    bal_log, dre_log, op_log = gerar_dados_fox_log()
    bal_fx, dre_fx, op_fx = gerar_dados_clube_fx()
    bal_consolidado, dre_consolidado = gerar_dados_consolidados()
    
    if opcao == "🏠 Visão Consolidada":
        st.markdown('<h2 class="company-header">📊 Visão Consolidada do Grupo</h2>', unsafe_allow_html=True)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Receita Líquida", "R$ 364.500 mil", "12.5%")
        with col2:
            st.metric("EBITDA", "R$ 41.000 mil", "8.2%")
        with col3:
            st.metric("Lucro Líquido", "R$ 6.800 mil", "-15.3%")
        with col4:
            st.metric("Margem EBITDA", "11.2%", "0.5pp")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            fig_receitas = criar_grafico_receitas()
            st.plotly_chart(fig_receitas, use_container_width=True)
        
        with col2:
            fig_commodities = criar_grafico_commodities()
            st.plotly_chart(fig_commodities, use_container_width=True)
        
        # Demonstrações consolidadas
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📊 Balanço Consolidado", "📈 DRE Consolidada"])
        
        with tab1:
            exibir_balanco(bal_consolidado, "Grupo FOX SA")
        
        with tab2:
            exibir_dre(dre_consolidado, "Grupo FOX SA")
    
    elif opcao == "🌾 Fox Grãos":
        st.markdown('<h2 class="company-header">🌾 Fox Grãos - Comercialização e Logística</h2>', unsafe_allow_html=True)
        
        # Tags de commodities
        st.markdown("""
        <div>
            <span class="commodity-tag">Soja</span>
            <span class="commodity-tag">Milho</span>
            <span class="commodity-tag">Sorgo</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Volume Total", "88.000 ton/ano")
        with col2:
            st.metric("Receita Líquida", "R$ 262.000 mil")
        with col3:
            st.metric("Margem Bruta", "19.8%")
        with col4:
            st.metric("Capacidade Armazenagem", "40.000 ton")
        
        # Dados por commodity
        st.markdown("### 📦 Performance por Commodity")
        
        commodity_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Volume (ton)': [45000, 35000, 8000],
            'Preço Médio Compra (R$/ton)': [4200, 2800, 2600],
            'Preço Médio Venda (R$/ton)': [4350, 2920, 2710],
            'Margem (R$/ton)': [150, 120, 110],
            'Estoque Atual (ton)': [12000, 8000, 2000]
        })
        
        st.dataframe(commodity_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balanço Patrimonial", "📈 DRE"])
        
        with tab1:
            exibir_balanco(bal_graos, "Fox Grãos")
        
        with tab2:
            exibir_dre(dre_graos, "Fox Grãos")
    
    elif opcao == "🚛 Fox Log":
        st.markdown('<h2 class="company-header">🚛 Fox Log - Transporte de Grãos e Insumos</h2>', unsafe_allow_html=True)
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Frota Total", "45 veículos")
        with col2:
            st.metric("Km/mês", "180.000 km")
        with col3:
            st.metric("Taxa Ocupação", "78%")
        with col4:
            st.metric("Receita Líquida", "R$ 79.500 mil")
        
        # Dados de transporte por commodity
        st.markdown("### 🚛 Transporte por Commodity")
        
        transporte_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo', 'Insumos'],
            'Volume Mensal (ton)': [8500, 6200, 1800, 2500],
            'Receita por Ton (R$)': [85, 90, 88, 120],
            'Receita Mensal (R$ mil)': [722.5, 558, 158.4, 300]
        })
        
        st.dataframe(transporte_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balanço Patrimonial", "📈 DRE"])
        
        with tab1:
            exibir_balanco(bal_log, "Fox Log")
        
        with tab2:
            exibir_dre(dre_log, "Fox Log")
    
    elif opcao == "💼 Clube FX":
        st.markdown('<h2 class="company-header">💼 Clube FX - Consultoria de Comercialização</h2>', unsafe_allow_html=True)
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Clientes Ativos", "85")
        with col2:
            st.metric("Receita/Cliente", "R$ 270 mil/ano")
        with col3:
            st.metric("Taxa Retenção", "82%")
        with col4:
            st.metric("Valor Hora", "R$ 180")
        
        # Dados de assessoria por commodity
        st.markdown("### 💡 Assessoria por Commodity")
        
        assessoria_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Volume Assessorado (ton/ano)': [125000, 95000, 25000],
            'Comissão Média (R$/ton)': [12, 15, 14],
            'Receita Anual (R$ mil)': [1500, 1425, 350]
        })
        
        st.dataframe(assessoria_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balanço Patrimonial", "📈 DRE"])
        
        with tab1:
            exibir_balanco(bal_fx, "Clube FX")
        
        with tab2:
            exibir_dre(dre_fx, "Clube FX")
    
    elif opcao == "📊 Análise por Commodity":
        st.markdown('<h2 class="company-header">📊 Análise por Commodity</h2>', unsafe_allow_html=True)
        
        # Comparativo de volumes
        commodity_volumes = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Fox Grãos (ton)': [45000, 35000, 8000],
            'Fox Log (ton/mês)': [8500, 6200, 1800],
            'Clube FX Assessoria (ton)': [125000, 95000, 25000]
        })
        
        st.markdown("### 📦 Volume por Commodity e Empresa")
        st.dataframe(commodity_volumes, use_container_width=True)
        
        # Gráfico de margens
        fig_margens = px.bar(
            x=['Soja', 'Milho', 'Sorgo'],
            y=[150, 120, 110],
            title="Margem por Tonelada - Fox Grãos (R$/ton)",
            color=['Soja', 'Milho', 'Sorgo'],
            color_discrete_sequence=['#8B4513', '#FFD700', '#CD853F']
        )
        st.plotly_chart(fig_margens, use_container_width=True)
        
        # Análise de preços
        st.markdown("### 💰 Análise de Preços")
        precos_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Preço Compra (R$/ton)': [4200, 2800, 2600],
            'Preço Venda (R$/ton)': [4350, 2920, 2710],
            'Spread (%)': [3.6, 4.3, 4.2]
        })
        
        st.dataframe(precos_data, use_container_width=True)
    
    elif opcao == "📈 Indicadores Comparativos":
        st.markdown('<h2 class="company-header">📈 Indicadores Financeiros Comparativos</h2>', unsafe_allow_html=True)
        
        # Calcular indicadores para cada empresa
        ind_graos = calcular_indicadores(bal_graos, dre_graos)
        ind_log = calcular_indicadores(bal_log, dre_log)
        ind_fx = calcular_indicadores(bal_fx, dre_fx)
        ind_consolidado = calcular_indicadores(bal_consolidado, dre_consolidado)
        
        # Criar DataFrame comparativo
        indicadores_df = pd.DataFrame({
            'Indicador': list(ind_graos.keys()),
            'Fox Grãos': [f"{v:.2f}" for v in ind_graos.values()],
            'Fox Log': [f"{v:.2f}" for v in ind_log.values()],
            'Clube FX': [f"{v:.2f}" for v in ind_fx.values()],
            'Consolidado': [f"{v:.2f}" for v in ind_consolidado.values()]
        })
        
        st.dataframe(indicadores_df, use_container_width=True)
        
        # Gráficos de indicadores
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de margens
            margens_data = pd.DataFrame({
                'Empresa': ['Fox Grãos', 'Fox Log', 'Clube FX'],
                'Margem Bruta': [ind_graos['Margem Bruta (%)'], ind_log['Margem Bruta (%)'], ind_fx['Margem Bruta (%)']],
                'Margem EBITDA': [ind_graos['Margem EBITDA (%)'], ind_log['Margem EBITDA (%)'], ind_fx['Margem EBITDA (%)']],
                'Margem Líquida': [ind_graos['Margem Líquida (%)'], ind_log['Margem Líquida (%)'], ind_fx['Margem Líquida (%)']]
            })
            
            fig_margens = px.bar(
                margens_data.melt(id_vars='Empresa', var_name='Tipo', value_name='Margem'),
                x='Empresa', y='Margem', color='Tipo',
                title="Comparativo de Margens (%)",
                barmode='group'
            )
            st.plotly_chart(fig_margens, use_container_width=True)
        
        with col2:
            # Gráfico de liquidez e endividamento
            liquidez_data = pd.DataFrame({
                'Empresa': ['Fox Grãos', 'Fox Log', 'Clube FX'],
                'Liquidez Corrente': [ind_graos['Liquidez Corrente'], ind_log['Liquidez Corrente'], ind_fx['Liquidez Corrente']],
                'Endividamento Total': [ind_graos['Endividamento Total'], ind_log['Endividamento Total'], ind_fx['Endividamento Total']]
            })
            
            fig_liquidez = px.bar(
                liquidez_data.melt(id_vars='Empresa', var_name='Indicador', value_name='Valor'),
                x='Empresa', y='Valor', color='Indicador',
                title="Liquidez e Endividamento",
                barmode='group'
            )
            st.plotly_chart(fig_liquidez, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**FOX SA** - Board de Gestão | Dados simulados para demonstração")

if __name__ == "__main__":
    main()

