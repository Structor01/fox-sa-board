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
    page_title="FOX SA - Investment Board",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderno inspirado no dashboard de exemplo
st.markdown("""
<style>
    /* Importar fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Container principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header principal moderno */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: left;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #8b949e;
        font-weight: 400;
        margin-bottom: 2rem;
        text-align: left;
    }
    
    /* Cards de métricas modernos */
    .metric-card-modern {
        background: linear-gradient(135deg, #21262d 0%, #30363d 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-modern:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
        border-color: #58a6ff;
    }
    
    .metric-card-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #58a6ff, #7c3aed, #f97316);
    }
    
    /* Métricas com estilo moderno */
    .stMetric {
        background: transparent;
        border: none;
        padding: 0;
    }
    
    .stMetric label {
        color: #8b949e !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stMetric div[data-testid="metric-container"] > div:first-child {
        color: #ffffff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        margin-bottom: 0.25rem !important;
    }
    
    .stMetric div[data-testid="metric-container"] > div:nth-child(2) {
        color: #7c3aed !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-right: 1px solid #30363d;
    }
    
    .css-1d391kg .stSelectbox label {
        color: #f0f6fc !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.25);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(88, 166, 255, 0.4);
    }
    
    /* Tabelas modernas */
    .stDataFrame {
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stDataFrame table {
        background: transparent !important;
        color: #f0f6fc !important;
    }
    
    .stDataFrame th {
        background: #30363d !important;
        color: #f0f6fc !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border-bottom: 1px solid #21262d !important;
        padding: 1rem !important;
    }
    
    .stDataFrame td {
        background: transparent !important;
        color: #f0f6fc !important;
        border-bottom: 1px solid #30363d !important;
        font-size: 0.875rem !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stDataFrame tr:hover td {
        background: rgba(88, 166, 255, 0.1) !important;
    }
    
    /* Headers de seção */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f0f6fc;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #30363d;
    }
    
    /* Tags de commodity modernas */
    .commodity-tag-modern {
        background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 100%);
        color: #ffffff;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.25);
        transition: all 0.3s ease;
    }
    
    .commodity-tag-modern:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(88, 166, 255, 0.4);
    }
    
    /* Gráficos com fundo moderno */
    .js-plotly-plot {
        background: #21262d !important;
        border-radius: 12px !important;
        border: 1px solid #30363d !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Alertas modernos */
    .stAlert {
        background: linear-gradient(135deg, #21262d 0%, #30363d 100%) !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        color: #f0f6fc !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        border: 1px solid #2ea043 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #da3633 0%, #f85149 100%) !important;
        border: 1px solid #f85149 !important;
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        background: #21262d;
        border-radius: 8px;
        padding: 0.25rem;
        border: 1px solid #30363d;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8b949e;
        border-radius: 6px;
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #58a6ff 0%, #7c3aed 100%);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(88, 166, 255, 0.25);
    }
    
    /* Esconder elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Animações suaves */
    .stApp > div {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .metric-card-modern {
            margin: 0.25rem 0;
            padding: 1rem;
        }
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #161b22;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #58a6ff;
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

# Função para criar gráfico de barras moderno
def criar_grafico_receitas():
    empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
    receitas = [262000, 79500, 23000]
    
    fig = px.bar(
        x=empresas, 
        y=receitas,
        title="Revenue by Company (R$ thousands)",
        color=empresas,
        color_discrete_sequence=['#58a6ff', '#7c3aed', '#f97316']
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f6fc', family='Inter'),
        title=dict(
            font=dict(size=18, color='#f0f6fc'),
            x=0.02,
            y=0.95
        ),
        xaxis=dict(
            showgrid=False,
            showline=False,
            color='#8b949e'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(139, 148, 158, 0.1)',
            showline=False,
            color='#8b949e'
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# Função para criar gráfico de pizza moderno
def criar_grafico_commodities():
    commodities = ['Soja', 'Milho', 'Sorgo']
    volumes = [45000, 35000, 8000]
    
    fig = px.pie(
        values=volumes, 
        names=commodities,
        title="Commodity Distribution",
        color_discrete_sequence=['#58a6ff', '#7c3aed', '#f97316']
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f6fc', family='Inter'),
        title=dict(
            font=dict(size=18, color='#f0f6fc'),
            x=0.02,
            y=0.95
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(color='#f0f6fc')
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# Função para criar gráfico de heatmap moderno
def criar_heatmap_performance():
    # Dados simulados de performance mensal
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
    
    # Matriz de performance (valores simulados)
    performance = [
        [85, 92, 78, 88, 95, 90],  # Fox Grãos
        [78, 85, 82, 79, 88, 85],  # Fox Log
        [92, 88, 95, 90, 85, 92]   # Clube FX
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=performance,
        x=meses,
        y=empresas,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(
            title="Performance %",
            titlefont=dict(color='#f0f6fc'),
            tickfont=dict(color='#f0f6fc')
        )
    ))
    
    fig.update_layout(
        title="Monthly Performance Heatmap",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f6fc', family='Inter'),
        title=dict(
            font=dict(size=18, color='#f0f6fc'),
            x=0.02,
            y=0.95
        ),
        xaxis=dict(color='#8b949e'),
        yaxis=dict(color='#8b949e'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# Função para exibir balanço patrimonial
def exibir_balanco(balanco, empresa):
    st.markdown(f'<h3 class="section-header">📊 Balanço Patrimonial - {empresa}</h3>', unsafe_allow_html=True)
    
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
    st.markdown(f'<h3 class="section-header">📈 Demonstração do Resultado - {empresa}</h3>', unsafe_allow_html=True)
    
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
    
    # Header principal moderno
    st.markdown('<h1 class="main-header">🌾 FOX SA Investment Board</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Comprehensive financial dashboard for agribusiness management</p>', unsafe_allow_html=True)
    
    # Sidebar com informações do usuário
    show_user_info()
    
    # Sidebar de navegação
    st.sidebar.title("📋 Navigation")
    
    # Obter dados do usuário atual
    current_user = get_current_user()
    
    # Opções de menu baseadas no perfil do usuário
    menu_options = ["🏠 Consolidated View"]
    
    # Adicionar opções baseadas em permissões
    if check_permission("viewer"):
        menu_options.extend([
            "🌾 Fox Grãos", 
            "🚛 Fox Log", 
            "💼 Clube FX", 
            "📊 Commodity Analysis"
        ])
    
    if check_permission("manager"):
        menu_options.append("📈 Comparative Indicators")
    
    # Adicionar seção de administração para admins
    if check_permission("admin"):
        menu_options.append("⚙️ Administration")
    
    opcao = st.sidebar.selectbox("Select view:", menu_options)
    
    # Carregar dados
    bal_graos, dre_graos, comm_graos = gerar_dados_fox_graos()
    bal_log, dre_log, op_log = gerar_dados_fox_log()
    bal_fx, dre_fx, op_fx = gerar_dados_clube_fx()
    bal_consolidado, dre_consolidado = gerar_dados_consolidados()
    
    if opcao == "🏠 Consolidated View":
        st.markdown('<h2 class="section-header">📊 Group Overview</h2>', unsafe_allow_html=True)
        
        # Métricas principais em cards modernos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Net Revenue", "R$ 364.5M", "12.5%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("EBITDA", "R$ 41.0M", "8.2%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Net Profit", "R$ 6.8M", "-15.3%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("EBITDA Margin", "11.2%", "0.5pp")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos modernos
        col1, col2 = st.columns(2)
        
        with col1:
            fig_receitas = criar_grafico_receitas()
            st.plotly_chart(fig_receitas, use_container_width=True)
        
        with col2:
            fig_commodities = criar_grafico_commodities()
            st.plotly_chart(fig_commodities, use_container_width=True)
        
        # Heatmap de performance
        st.markdown('<h3 class="section-header">📈 Performance Overview</h3>', unsafe_allow_html=True)
        fig_heatmap = criar_heatmap_performance()
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Demonstrações consolidadas
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["📊 Consolidated Balance Sheet", "📈 Consolidated P&L"])
        
        with tab1:
            exibir_balanco(bal_consolidado, "FOX SA Group")
        
        with tab2:
            exibir_dre(dre_consolidado, "FOX SA Group")
    
    elif opcao == "🌾 Fox Grãos":
        st.markdown('<h2 class="section-header">🌾 Fox Grãos - Grain Trading & Logistics</h2>', unsafe_allow_html=True)
        
        # Tags de commodities modernas
        st.markdown("""
        <div style="margin: 1.5rem 0;">
            <span class="commodity-tag-modern">Soja</span>
            <span class="commodity-tag-modern">Milho</span>
            <span class="commodity-tag-modern">Sorgo</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Total Volume", "88,000 tons/year")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Net Revenue", "R$ 262.0M")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Gross Margin", "19.8%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Storage Capacity", "40,000 tons")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Dados por commodity
        st.markdown('<h3 class="section-header">📦 Commodity Performance</h3>', unsafe_allow_html=True)
        
        commodity_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Volume (tons)': [45000, 35000, 8000],
            'Avg Buy Price (R$/ton)': [4200, 2800, 2600],
            'Avg Sell Price (R$/ton)': [4350, 2920, 2710],
            'Margin (R$/ton)': [150, 120, 110],
            'Current Stock (tons)': [12000, 8000, 2000]
        })
        
        st.dataframe(commodity_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balance Sheet", "📈 P&L Statement"])
        
        with tab1:
            exibir_balanco(bal_graos, "Fox Grãos")
        
        with tab2:
            exibir_dre(dre_graos, "Fox Grãos")
    
    elif opcao == "🚛 Fox Log":
        st.markdown('<h2 class="section-header">🚛 Fox Log - Grain & Input Transportation</h2>', unsafe_allow_html=True)
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Fleet Size", "45 vehicles")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Monthly KM", "180,000 km")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Utilization Rate", "78%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Net Revenue", "R$ 79.5M")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Dados de transporte por commodity
        st.markdown('<h3 class="section-header">🚛 Transportation by Commodity</h3>', unsafe_allow_html=True)
        
        transporte_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo', 'Inputs'],
            'Monthly Volume (tons)': [8500, 6200, 1800, 2500],
            'Revenue per Ton (R$)': [85, 90, 88, 120],
            'Monthly Revenue (R$ thousands)': [722.5, 558, 158.4, 300]
        })
        
        st.dataframe(transporte_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balance Sheet", "📈 P&L Statement"])
        
        with tab1:
            exibir_balanco(bal_log, "Fox Log")
        
        with tab2:
            exibir_dre(dre_log, "Fox Log")
    
    elif opcao == "💼 Clube FX":
        st.markdown('<h2 class="section-header">💼 Clube FX - Trading Consultancy</h2>', unsafe_allow_html=True)
        
        # Métricas operacionais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Active Clients", "85")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Revenue/Client", "R$ 270k/year")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Retention Rate", "82%")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Hourly Rate", "R$ 180")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Dados de assessoria por commodity
        st.markdown('<h3 class="section-header">💡 Advisory by Commodity</h3>', unsafe_allow_html=True)
        
        assessoria_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Volume Advised (tons/year)': [125000, 95000, 25000],
            'Avg Commission (R$/ton)': [12, 15, 14],
            'Annual Revenue (R$ thousands)': [1500, 1425, 350]
        })
        
        st.dataframe(assessoria_data, use_container_width=True)
        
        # Demonstrações financeiras
        tab1, tab2 = st.tabs(["📊 Balance Sheet", "📈 P&L Statement"])
        
        with tab1:
            exibir_balanco(bal_fx, "Clube FX")
        
        with tab2:
            exibir_dre(dre_fx, "Clube FX")
    
    elif opcao == "📊 Commodity Analysis":
        st.markdown('<h2 class="section-header">📊 Commodity Analysis</h2>', unsafe_allow_html=True)
        
        # Comparativo de volumes
        commodity_volumes = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Fox Grãos (tons)': [45000, 35000, 8000],
            'Fox Log (tons/month)': [8500, 6200, 1800],
            'Clube FX Advisory (tons)': [125000, 95000, 25000]
        })
        
        st.markdown('<h3 class="section-header">📦 Volume by Commodity and Company</h3>', unsafe_allow_html=True)
        st.dataframe(commodity_volumes, use_container_width=True)
        
        # Gráfico de margens moderno
        fig_margens = px.bar(
            x=['Soja', 'Milho', 'Sorgo'],
            y=[150, 120, 110],
            title="Margin per Ton - Fox Grãos (R$/ton)",
            color=['Soja', 'Milho', 'Sorgo'],
            color_discrete_sequence=['#58a6ff', '#7c3aed', '#f97316']
        )
        
        fig_margens.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f0f6fc', family='Inter'),
            title=dict(
                font=dict(size=18, color='#f0f6fc'),
                x=0.02,
                y=0.95
            ),
            xaxis=dict(
                showgrid=False,
                showline=False,
                color='#8b949e'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(139, 148, 158, 0.1)',
                showline=False,
                color='#8b949e'
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig_margens, use_container_width=True)
        
        # Análise de preços
        st.markdown('<h3 class="section-header">💰 Price Analysis</h3>', unsafe_allow_html=True)
        precos_data = pd.DataFrame({
            'Commodity': ['Soja', 'Milho', 'Sorgo'],
            'Buy Price (R$/ton)': [4200, 2800, 2600],
            'Sell Price (R$/ton)': [4350, 2920, 2710],
            'Spread (%)': [3.6, 4.3, 4.2]
        })
        
        st.dataframe(precos_data, use_container_width=True)
    
    elif opcao == "📈 Comparative Indicators":
        if not check_permission("manager"):
            st.error("🚫 Access denied! This section requires Manager permission or higher.")
            st.info("Contact the administrator to request access.")
            return
            
        st.markdown('<h2 class="section-header">📈 Comparative Financial Indicators</h2>', unsafe_allow_html=True)
        
        # Calcular indicadores para cada empresa
        ind_graos = calcular_indicadores(bal_graos, dre_graos)
        ind_log = calcular_indicadores(bal_log, dre_log)
        ind_fx = calcular_indicadores(bal_fx, dre_fx)
        ind_consolidado = calcular_indicadores(bal_consolidado, dre_consolidado)
        
        # Criar DataFrame comparativo
        indicadores_df = pd.DataFrame({
            'Indicator': list(ind_graos.keys()),
            'Fox Grãos': [f"{v:.2f}" for v in ind_graos.values()],
            'Fox Log': [f"{v:.2f}" for v in ind_log.values()],
            'Clube FX': [f"{v:.2f}" for v in ind_fx.values()],
            'Consolidated': [f"{v:.2f}" for v in ind_consolidado.values()]
        })
        
        st.dataframe(indicadores_df, use_container_width=True)
        
        # Gráficos de indicadores modernos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de margens
            margens_data = pd.DataFrame({
                'Company': ['Fox Grãos', 'Fox Log', 'Clube FX'],
                'Gross Margin': [ind_graos['Margem Bruta (%)'], ind_log['Margem Bruta (%)'], ind_fx['Margem Bruta (%)']],
                'EBITDA Margin': [ind_graos['Margem EBITDA (%)'], ind_log['Margem EBITDA (%)'], ind_fx['Margem EBITDA (%)']],
                'Net Margin': [ind_graos['Margem Líquida (%)'], ind_log['Margem Líquida (%)'], ind_fx['Margem Líquida (%)']]
            })
            
            fig_margens = px.bar(
                margens_data.melt(id_vars='Company', var_name='Type', value_name='Margin'),
                x='Company', y='Margin', color='Type',
                title="Margin Comparison (%)",
                barmode='group',
                color_discrete_sequence=['#58a6ff', '#7c3aed', '#f97316']
            )
            
            fig_margens.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f0f6fc', family='Inter'),
                title=dict(
                    font=dict(size=18, color='#f0f6fc'),
                    x=0.02,
                    y=0.95
                ),
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    color='#8b949e'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(139, 148, 158, 0.1)',
                    showline=False,
                    color='#8b949e'
                ),
                legend=dict(font=dict(color='#f0f6fc')),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig_margens, use_container_width=True)
        
        with col2:
            # Gráfico de liquidez e endividamento
            liquidez_data = pd.DataFrame({
                'Company': ['Fox Grãos', 'Fox Log', 'Clube FX'],
                'Current Ratio': [ind_graos['Liquidez Corrente'], ind_log['Liquidez Corrente'], ind_fx['Liquidez Corrente']],
                'Total Debt': [ind_graos['Endividamento Total'], ind_log['Endividamento Total'], ind_fx['Endividamento Total']]
            })
            
            fig_liquidez = px.bar(
                liquidez_data.melt(id_vars='Company', var_name='Indicator', value_name='Value'),
                x='Company', y='Value', color='Indicator',
                title="Liquidity and Debt",
                barmode='group',
                color_discrete_sequence=['#58a6ff', '#f97316']
            )
            
            fig_liquidez.update_layout(
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f0f6fc', family='Inter'),
                title=dict(
                    font=dict(size=18, color='#f0f6fc'),
                    x=0.02,
                    y=0.95
                ),
                xaxis=dict(
                    showgrid=False,
                    showline=False,
                    color='#8b949e'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(139, 148, 158, 0.1)',
                    showline=False,
                    color='#8b949e'
                ),
                legend=dict(font=dict(color='#f0f6fc')),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig_liquidez, use_container_width=True)
    
    elif opcao == "⚙️ Administration":
        if not check_permission("admin"):
            st.error("🚫 Access denied! This section requires Administrator permission.")
            return
            
        st.markdown('<h2 class="section-header">⚙️ Administration Panel</h2>', unsafe_allow_html=True)
        
        # Informações do sistema
        st.markdown('<h3 class="section-header">📊 System Information</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Registered Users", "4")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Active Sessions", "1")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card-modern">', unsafe_allow_html=True)
            st.metric("Last Update", "Now")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logs de acesso
        st.markdown('<h3 class="section-header">📝 Recent Access Logs</h3>', unsafe_allow_html=True)
        logs_data = pd.DataFrame({
            'Timestamp': ['2024-06-24 15:45:00', '2024-06-24 15:43:00', '2024-06-24 15:40:00'],
            'User': [current_user['username'], 'gestor', 'viewer'],
            'Action': ['Login', 'Viewed Fox Grãos', 'Login'],
            'IP': ['192.168.1.100', '192.168.1.101', '192.168.1.102']
        })
        st.dataframe(logs_data, use_container_width=True)
        
        # Configurações de segurança
        st.markdown('<h3 class="section-header">🔐 Security Settings</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Force logout after inactivity", value=True)
            st.checkbox("Automatic backup", value=True)
        
        with col2:
            st.selectbox("Log level", ["Info", "Debug", "Warning", "Error"])
            st.selectbox("Backup frequency", ["Daily", "Weekly", "Monthly"])

if __name__ == "__main__":
    main()

