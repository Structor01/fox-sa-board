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

# CSS customizado para design premium
st.markdown("""
<style>
    /* Reset e configurações globais */
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 50%, #0f0f0f 100%);
        color: #ffffff;
    }
    
    /* Header principal premium */
    .main-header {
        font-size: 3.5rem;
        font-weight: 300;
        color: #ffffff;
        text-align: center;
        margin: 2rem 0;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
        letter-spacing: 2px;
        background: linear-gradient(45deg, #ffffff, #c0c0c0, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(255, 255, 255, 0.3); }
        to { text-shadow: 0 0 40px rgba(255, 255, 255, 0.6); }
    }
    
    /* Headers de seção premium */
    .company-header {
        font-size: 2.2rem;
        font-weight: 200;
        color: #c0c0c0;
        margin: 2rem 0 1.5rem 0;
        padding: 1rem 0;
        border-bottom: 2px solid rgba(192, 192, 192, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Cards de métricas premium */
    .metric-card-premium {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        border: 1px solid rgba(192, 192, 192, 0.2);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 10px 30px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .metric-card-premium:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(192, 192, 192, 0.4);
    }
    
    /* Sidebar premium */
    .css-1d391kg {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
        border-right: 1px solid rgba(192, 192, 192, 0.2);
    }
    
    /* Botões premium */
    .stButton > button {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        color: #ffffff;
        border: 1px solid rgba(192, 192, 192, 0.3);
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 300;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
        border-color: rgba(192, 192, 192, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Métricas com estilo premium */
    .stMetric {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        border: 1px solid rgba(192, 192, 192, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: scale(1.02);
        border-color: rgba(192, 192, 192, 0.4);
    }
    
    .stMetric label {
        color: #c0c0c0 !important;
        font-size: 0.9rem !important;
        font-weight: 300 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stMetric div[data-testid="metric-container"] > div:first-child {
        color: #ffffff !important;
        font-size: 2.5rem !important;
        font-weight: 200 !important;
    }
    
    /* Tabelas premium */
    .stDataFrame {
        background: rgba(26, 26, 26, 0.8);
        border: 1px solid rgba(192, 192, 192, 0.2);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        background: transparent !important;
        color: #ffffff !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a) !important;
        color: #c0c0c0 !important;
        font-weight: 300 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border-bottom: 1px solid rgba(192, 192, 192, 0.3) !important;
    }
    
    .stDataFrame td {
        background: rgba(26, 26, 26, 0.5) !important;
        color: #ffffff !important;
        border-bottom: 1px solid rgba(192, 192, 192, 0.1) !important;
    }
    
    /* Selectbox premium */
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid rgba(192, 192, 192, 0.3);
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Tags de commodity premium */
    .commodity-tag-premium {
        background: linear-gradient(45deg, #2a2a2a, #3a3a3a);
        color: #c0c0c0;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
        border: 1px solid rgba(192, 192, 192, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 300;
        transition: all 0.3s ease;
    }
    
    .commodity-tag-premium:hover {
        background: linear-gradient(45deg, #3a3a3a, #4a4a4a);
        border-color: rgba(192, 192, 192, 0.5);
        transform: scale(1.05);
    }
    
    /* Informações de usuário premium */
    .user-info-premium {
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        border: 1px solid rgba(192, 192, 192, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Gráficos com fundo escuro */
    .js-plotly-plot {
        background: transparent !important;
    }
    
    /* Animações suaves */
    .stApp > div {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Rodapé premium */
    .footer-premium {
        background: linear-gradient(145deg, #0a0a0a, #1a1a1a);
        border-top: 1px solid rgba(192, 192, 192, 0.2);
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        color: #c0c0c0;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Efeitos de hover para elementos interativos */
    .element-container:hover {
        transition: all 0.3s ease;
    }
    
    /* Estilo para login premium */
    .login-container-premium {
        max-width: 450px;
        margin: 0 auto;
        padding: 3rem;
        background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
        border: 1px solid rgba(192, 192, 192, 0.3);
        border-radius: 20px;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.7),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin-top: 5rem;
        backdrop-filter: blur(20px);
    }
    
    .login-header-premium {
        text-align: center;
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 200;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
        letter-spacing: 2px;
    }
    
    /* Inputs premium */
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        border: 1px solid rgba(192, 192, 192, 0.3);
        border-radius: 8px;
        color: #ffffff;
        padding: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(192, 192, 192, 0.6);
        box-shadow: 0 0 10px rgba(192, 192, 192, 0.3);
    }
    
    /* Esconder elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsividade premium */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .company-header {
            font-size: 1.8rem;
        }
        .metric-card-premium {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuração de tema premium para gráficos
def get_premium_theme():
    """Retorna configuração de tema premium para gráficos Plotly"""
    return {
        'layout': {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(26,26,26,0.8)',
            'font': {
                'color': '#ffffff',
                'family': 'Arial, sans-serif',
                'size': 12
            },
            'title': {
                'font': {
                    'color': '#ffffff',
                    'size': 18,
                    'family': 'Arial, sans-serif'
                },
                'x': 0.5,
                'xanchor': 'center'
            },
            'xaxis': {
                'gridcolor': 'rgba(192,192,192,0.2)',
                'linecolor': 'rgba(192,192,192,0.3)',
                'tickcolor': 'rgba(192,192,192,0.3)',
                'tickfont': {'color': '#c0c0c0'},
                'titlefont': {'color': '#c0c0c0'}
            },
            'yaxis': {
                'gridcolor': 'rgba(192,192,192,0.2)',
                'linecolor': 'rgba(192,192,192,0.3)',
                'tickcolor': 'rgba(192,192,192,0.3)',
                'tickfont': {'color': '#c0c0c0'},
                'titlefont': {'color': '#c0c0c0'}
            },
            'legend': {
                'font': {'color': '#c0c0c0'},
                'bgcolor': 'rgba(26,26,26,0.8)',
                'bordercolor': 'rgba(192,192,192,0.3)',
                'borderwidth': 1
            },
            'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60}
        }
    }

# Paleta de cores premium para gráficos
PREMIUM_COLORS = [
    '#c0c0c0',  # Prata principal
    '#ffffff',  # Branco
    '#808080',  # Cinza médio
    '#a0a0a0',  # Prata claro
    '#606060',  # Cinza escuro
    '#d0d0d0',  # Prata muito claro
    '#404040',  # Cinza muito escuro
    '#e0e0e0'   # Quase branco
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

# Função para criar gráfico de barras comparativo premium
def criar_grafico_receitas():
    empresas = ['Fox Grãos', 'Fox Log', 'Clube FX']
    receitas = [262000, 79500, 23000]
    
    fig = px.bar(
        x=empresas, 
        y=receitas,
        title="REVENUE BY COMPANY (R$ THOUSAND)",
        color=empresas,
        color_discrete_sequence=PREMIUM_COLORS[:3]
    )
    
    # Aplicar tema premium
    theme = get_premium_theme()
    fig.update_layout(**theme['layout'])
    fig.update_layout(
        showlegend=False, 
        height=400,
        title_font_size=16,
        title_font_color='#c0c0c0'
    )
    
    # Customizar barras
    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside',
        textfont_color='#c0c0c0',
        marker_line_color='rgba(192,192,192,0.3)',
        marker_line_width=1
    )
    
    return fig

# Função para criar gráfico de commodities premium
def criar_grafico_commodities():
    commodities = ['Soja', 'Milho', 'Sorgo']
    volumes = [45000, 35000, 8000]
    
    fig = px.pie(
        values=volumes,
        names=commodities,
        title="COMMODITY VOLUME DISTRIBUTION (TONS/YEAR)",
        color_discrete_sequence=PREMIUM_COLORS[:3]
    )
    
    # Aplicar tema premium
    theme = get_premium_theme()
    fig.update_layout(**theme['layout'])
    fig.update_layout(
        height=400,
        title_font_size=16,
        title_font_color='#c0c0c0'
    )
    
    # Customizar pizza
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_color='#000000',
        textfont_size=12,
        marker_line_color='rgba(0,0,0,0.8)',
        marker_line_width=2
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
    # Verificar autenticação
    if not check_authentication():
        show_login_page()
        return
    
    # Título principal premium
    st.markdown('<h1 class="main-header">🌾 FOX SA - INVESTMENT BOARD</h1>', unsafe_allow_html=True)
    
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
        
        # Tags de commodities premium
        st.markdown("""
        <div style="margin: 1rem 0;">
            <span class="commodity-tag-premium">SOJA</span>
            <span class="commodity-tag-premium">MILHO</span>
            <span class="commodity-tag-premium">SORGO</span>
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
    
    # Rodapé premium
    st.markdown('<div class="footer-premium">', unsafe_allow_html=True)
    
    # Informações de segurança baseadas no perfil
    security_info = f"🔐 **SECURE SESSION** | User: {current_user['name']} ({current_user['role'].title()}) | "
    
    if check_permission("admin"):
        security_info += "FULL ACCESS"
    elif check_permission("manager"):
        security_info += "MANAGEMENT ACCESS"
    else:
        security_info += "VIEW ACCESS"
    
    st.markdown(security_info)
    st.markdown("**FOX SA** - AGRIBUSINESS INVESTMENT BOARD | Authenticated System | Demo Data for Presentation")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

