import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Importar sistema de autenticação
from auth import (
    check_authentication, 
    show_login_page, 
    show_user_info, 
    get_current_user,
    check_permission
)

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

# CSS minimalista inspirado em Steve Jobs
st.markdown("""
<style>
    /* Reset e configurações globais - Simplicidade extrema */
    .stApp {
        background: #000000;
        color: #ffffff;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* Header principal - Tipografia perfeita */
    .main-header {
        font-size: 3.2rem;
        font-weight: 100;
        color: #ffffff;
        text-align: center;
        margin: 3rem 0;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    /* Headers de seção - Minimalismo */
    .company-header {
        font-size: 1.8rem;
        font-weight: 200;
        color: #ffffff;
        margin: 3rem 0 2rem 0;
        padding: 0;
        border: none;
        letter-spacing: -0.5px;
    }
    
    /* Cards de métricas - Simplicidade */
    .metric-card-jobs {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }
    
    .metric-card-jobs:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Sidebar - Minimalismo total */
    .css-1d391kg {
        background: #000000;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Botões - Design Apple */
    .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 400;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        letter-spacing: 0;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Métricas - Estilo Apple com contraste perfeito */
    .stMetric {
        background: transparent;
        border: none;
        padding: 1rem 0;
        text-align: left;
    }
    
    .stMetric label {
        color: #ffffff !important;
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMetric div[data-testid="metric-container"] > div:first-child {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 200 !important;
        line-height: 1.1 !important;
    }
    
    .stMetric div[data-testid="metric-container"] > div:nth-child(2) {
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }
    
    /* Tabelas - Minimalismo com contraste perfeito */
    .stDataFrame {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        background: transparent !important;
        color: #ffffff !important;
    }
    
    .stDataFrame th {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 1rem !important;
    }
    
    .stDataFrame td {
        background: transparent !important;
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        font-size: 1rem !important;
        padding: 0.8rem 1rem !important;
    }
    
    /* Selectbox - Apple style com contraste perfeito */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        color: #ffffff;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    /* Sidebar - Minimalismo total com contraste */
    .css-1d391kg {
        background: #000000;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .css-1d391kg .stMarkdown {
        color: #ffffff !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: #ffffff !important;
    }
    
    .css-1d391kg p {
        color: #ffffff !important;
    }
    
    /* Tags de commodity - Minimalismo */
    .commodity-tag-jobs {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-size: 0.75rem;
        margin: 0.2rem;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Informações de usuário - Simplicidade com contraste perfeito */
    .user-info-jobs {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: left;
    }
    
    .user-info-jobs h1, .user-info-jobs h2, .user-info-jobs h3, .user-info-jobs h4 {
        color: #ffffff !important;
    }
    
    .user-info-jobs p, .user-info-jobs span, .user-info-jobs div {
        color: #ffffff !important;
    }
    
    /* Login container - Apple style */
    .login-container-jobs {
        max-width: 400px;
        margin: 0 auto;
        padding: 3rem 2rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-top: 8rem;
        backdrop-filter: blur(20px);
    }
    
    .login-header-jobs {
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 100;
        margin-bottom: 2rem;
        letter-spacing: -1px;
    }
    
    /* Inputs - Apple design */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: #ffffff;
        padding: 0.75rem;
        font-size: 0.9rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
    }
    
    /* Rodapé - Minimalismo total */
    .footer-jobs {
        background: transparent;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 0;
        margin-top: 4rem;
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 300;
        font-size: 0.8rem;
    }
    
    /* Esconder elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* ESTILOS GLOBAIS PARA CONTRASTE PERFEITO */
    .stApp, .stApp * {
        color: #ffffff !important;
    }
    
    /* Forçar texto branco em todos os elementos */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Elementos específicos do Streamlit */
    .stMarkdown {
        color: #ffffff !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    .stMarkdown p {
        color: #ffffff !important;
    }
    
    /* Sidebar específica */
    .css-1d391kg * {
        color: #ffffff !important;
    }
    
    /* Alertas e mensagens */
    .stAlert {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    .stSuccess {
        background: rgba(0, 255, 0, 0.1) !important;
        border: 1px solid rgba(0, 255, 0, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 0, 0, 0.3) !important;
        color: #ffffff !important;
    }
    
    .stWarning {
        background: rgba(255, 255, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 0, 0.3) !important;
        color: #ffffff !important;
    }
    
    /* Animação suave - Subtil como Apple */
    .stApp > div {
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Responsividade - Mobile first */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .company-header {
            font-size: 1.5rem;
        }
        .login-container-jobs {
            margin-top: 4rem;
            padding: 2rem 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuração de tema minimalista Steve Jobs para gráficos
def get_jobs_theme():
    """Retorna configuração de tema minimalista inspirado em Steve Jobs"""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'color': '#ffffff',
            'family': 'SF Pro Display, -apple-system, BlinkMacSystemFont, Helvetica Neue, Arial, sans-serif',
            'size': 14
        },
        'title': {
            'font': {
                'color': '#ffffff',
                'size': 24,
                'family': 'SF Pro Display, -apple-system, BlinkMacSystemFont, Helvetica Neue, Arial, sans-serif'
            },
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top'
        },
        'xaxis': {
            'showgrid': False,
            'showline': False,
            'showticklabels': True,
            'tickcolor': 'rgba(255,255,255,0.3)',
            'tickfont': {'color': '#ffffff', 'size': 12},
            'titlefont': {'color': '#ffffff', 'size': 14}
        },
        'yaxis': {
            'showgrid': True,
            'gridcolor': 'rgba(255,255,255,0.1)',
            'showline': False,
            'showticklabels': True,
            'tickcolor': 'rgba(255,255,255,0.3)',
            'tickfont': {'color': '#ffffff', 'size': 12},
            'titlefont': {'color': '#ffffff', 'size': 14}
        },
        'legend': {
            'font': {'color': '#ffffff', 'size': 12},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
            'borderwidth': 0
        },
        'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40}
    }

# Paleta de cores minimalista Steve Jobs
JOBS_COLORS = [
    '#ffffff',  # Branco puro - principal
    '#e5e5e7',  # Cinza muito claro
    '#d1d1d6',  # Cinza claro
    '#8e8e93',  # Cinza médio
    '#636366',  # Cinza escuro
    '#48484a',  # Cinza muito escuro
    '#1c1c1e',  # Quase preto
    '#000000'   # Preto puro
]

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

# Função para criar gráfico de barras mínimo absoluto
def criar_grafico_receitas():
    empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
    receitas = [262000, 79500, 23000]
    
    # Gráfico básico sem customizações
    fig = px.bar(x=empresas, y=receitas, title="Revenue by Company")
    
    # Apenas altura - sem outras configurações
    fig.update_layout(height=350)
    
    return fig

# Função para criar gráfico de pizza mínimo absoluto
def criar_grafico_commodities():
    commodities = ['Soja', 'Milho', 'Sorgo']
    volumes = [45000, 35000, 8000]
    
    # Gráfico básico sem customizações
    fig = px.pie(values=volumes, names=commodities, title="Commodity Distribution")
    
    # Apenas altura - sem outras configurações
    fig.update_layout(height=350)
    
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
    # Verificar autenticação
    if not check_authentication():
        show_login_page()
        return
    
    # Título principal minimalista Steve Jobs
    st.markdown('<h1 class="main-header">FOX SA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.6); font-size: 1.1rem; font-weight: 300; margin-bottom: 3rem; letter-spacing: 1px;">Investment Board</p>', unsafe_allow_html=True)
    
    # Sidebar com informações do usuário
    show_user_info()
    
    # Sidebar de navegação
    st.sidebar.title("📋 Navegação")
    
    # Obter dados do usuário atual
    current_user = get_current_user()
    
    # Opções de menu baseadas no perfil do usuário
    menu_options = ["🏠 Visão Consolidada"]
    
    # Adicionar opções baseadas em permissões
    if check_permission("viewer"):
        menu_options.extend([
            "🌾 Fox Grãos", 
            "🚛 Fox Log", 
            "💼 Clube FX", 
            "📊 Análise por Commodity"
        ])
    
    if check_permission("manager"):
        menu_options.append("📈 Indicadores Comparativos")
    
    # Adicionar seção de administração para admins
    if check_permission("admin"):
        menu_options.append("⚙️ Administração")
    
    opcao = st.sidebar.selectbox("Selecione a visualização:", menu_options)
    
    # Exibir informações do usuário no topo
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        st.info(f"👤 Logado como: **{current_user['name']}**")
    
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
        
        # Tags de commodities minimalistas
        st.markdown("""
        <div style="margin: 2rem 0;">
            <span class="commodity-tag-jobs">Soja</span>
            <span class="commodity-tag-jobs">Milho</span>
            <span class="commodity-tag-jobs">Sorgo</span>
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
        if not check_permission("manager"):
            st.error("🚫 Acesso negado! Esta seção requer permissão de Gestor ou superior.")
            st.info("Entre em contato com o administrador para solicitar acesso.")
            return
            
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
    
    elif opcao == "⚙️ Administração":
        if not check_permission("admin"):
            st.error("🚫 Acesso negado! Esta seção requer permissão de Administrador.")
            return
            
        st.markdown('<h2 class="company-header">⚙️ Painel de Administração</h2>', unsafe_allow_html=True)
        
        # Informações do sistema
        st.markdown("### 📊 Informações do Sistema")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Usuários Cadastrados", "4")
        with col2:
            st.metric("Sessões Ativas", "1")
        with col3:
            st.metric("Última Atualização", "Agora")
        
        # Logs de acesso
        st.markdown("### 📝 Logs de Acesso Recentes")
        logs_data = pd.DataFrame({
            'Timestamp': ['2024-06-24 14:05:00', '2024-06-24 14:03:00', '2024-06-24 14:00:00'],
            'Usuário': [current_user['username'], 'gestor', 'viewer'],
            'Ação': ['Login', 'Visualizou Fox Grãos', 'Login'],
            'IP': ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        })
        st.dataframe(logs_data, use_container_width=True)
        
        # Configurações de segurança
        st.markdown("### 🔐 Configurações de Segurança")
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Forçar logout após inatividade", value=True)
            st.checkbox("Log de todas as ações", value=True)
        
        with col2:
            st.checkbox("Notificar logins suspeitos", value=False)
            st.checkbox("Backup automático", value=True)
    
    # Rodapé minimalista Steve Jobs
    st.markdown('<div class="footer-jobs">', unsafe_allow_html=True)
    
    # Informações de segurança minimalistas
    security_info = f"Secure Session • {current_user['name']} ({current_user['role'].title()}) • "
    
    if check_permission("admin"):
        security_info += "Full Access"
    elif check_permission("manager"):
        security_info += "Management Access"
    else:
        security_info += "View Access"
    
    st.markdown(security_info)
    st.markdown("FOX SA Investment Board • Demo Data")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

