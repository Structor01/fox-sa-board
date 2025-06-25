import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from src.gerar_dados_fox import *
from src.auth import *

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

def configurar_pagina():
    """Configuração inicial da página"""
    st.set_page_config(
        page_title="FOX SA - Painel de Resultados em Tempo Real",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

# ============================================================================
# TELA DE BOAS-VINDAS
# ============================================================================

def tela_boas_vindas():
    """Tela de boas-vindas com filtros principais"""
    
    # Logo e título dinâmico
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; color: #C0C0C0;">🌾</div>
            <div style="font-size: 1.2rem; color: #FFD700; font-weight: 600;">FOX SA</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 2rem 0;">
            <h1 style="color: #FFFFFF; font-size: 2.5rem; margin: 0;">Painel de Resultados em Tempo Real</h1>
            <p style="color: #C0C0C0; font-size: 1.2rem; margin: 0.5rem 0;">Dashboard executivo para acompanhamento estratégico do agronegócio</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr style="margin: 2rem 0; border: 1px solid #333333;">', unsafe_allow_html=True)
    
    # Filtros principais
    st.markdown('<h3 style="color: #FFFFFF; margin-bottom: 1rem;">⚙️ Configurações do Dashboard</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.markdown("**📅 Período de Análise**")
        data_inicial = st.date_input(
            "Data Inicial:",
            value=datetime.now() - timedelta(days=365),
            key="data_inicial"
        )
        data_final = st.date_input(
            "Data Final:",
            value=datetime.now(),
            key="data_final"
        )
    
    with col2:
        st.markdown("**🏢 Unidades de Negócio**")
        fox_graos = st.checkbox("Fox Grãos (Trade & Logística)", value=True, key="fox_graos")
        fox_log = st.checkbox("Fox Log (Transporte & Insumos)", value=True, key="fox_log")
        clube_fx = st.checkbox("Clube FX (Consultoria)", value=True, key="clube_fx")
    
    with col3:
        st.markdown("**🔄 Status dos Dados**")
        ultima_atualizacao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        st.info(f"📊 Última atualização: {ultima_atualizacao}")
        
        if st.button("🔄 Atualizar Dados", key="refresh_welcome"):
            st.rerun()
    
    # Botão para acessar dashboard
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Acessar Dashboard Completo", key="access_dashboard", type="primary"):
            st.session_state.show_welcome = False
            st.rerun()
    
    return {
        'data_inicial': data_inicial,
        'data_final': data_final,
        'unidades': {
            'fox_graos': fox_graos,
            'fox_log': fox_log,
            'clube_fx': clube_fx
        }
    }

# ============================================================================
# VISÃO CONSOLIDADA
# ============================================================================

def visao_consolidada(dados_eda, dados_financeiros):
    """Dashboard geral consolidado"""
    
    st.markdown('<h2 style="color: #FFFFFF; border-bottom: 2px solid #C0C0C0; padding-bottom: 0.5rem;">📊 Visão Consolidada</h2>', unsafe_allow_html=True)
    
    # KPIs principais com alertas
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = [
        {'label': 'Receita Bruta', 'value': 'R$ 247M', 'delta': '+12.5%', 'color': '#90EE90'},
        {'label': 'EBITDA', 'value': 'R$ 89M', 'delta': '+8.3%', 'color': '#FFD700'},
        {'label': 'Fluxo de Caixa Op.', 'value': 'R$ 76M', 'delta': '+15.2%', 'color': '#C0C0C0'},
        {'label': 'Clientes Ativos', 'value': '1,247', 'delta': '+5.8%', 'color': '#87CEEB'}
    ]
    
    for i, kpi in enumerate(kpis):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #333333;
                text-align: center;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            ">
                <div style="color: #C0C0C0; font-size: 0.9rem; margin-bottom: 0.5rem;">{kpi['label']}</div>
                <div style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;">{kpi['value']}</div>
                <div style="color: {kpi['color']}; font-size: 0.9rem; font-weight: 600;">
                    ▲ {kpi['delta']} vs período anterior
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Receita x EBITDA (12 meses)
        fig_receita_ebitda = criar_grafico_receita_ebitda()
        st.plotly_chart(fig_receita_ebitda, use_container_width=True)
    
    with col2:
        # Investimento vs Capex
        fig_investimento_capex = criar_grafico_investimento_capex()
        st.plotly_chart(fig_investimento_capex, use_container_width=True)

def criar_grafico_receita_ebitda():
    """Gráfico de linha Receita x EBITDA"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    receita = [18.5, 19.2, 21.8, 20.1, 22.3, 24.1, 23.8, 25.2, 24.9, 26.1, 25.8, 27.2]
    ebitda = [6.8, 7.1, 8.2, 7.5, 8.9, 9.8, 9.2, 10.1, 9.8, 10.5, 10.2, 11.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=receita,
        mode='lines+markers',
        name='Receita Bruta',
        line=dict(color='#90EE90', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Receita: R$ %{y}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=ebitda,
        mode='lines+markers',
        name='EBITDA',
        line=dict(color='#FFD700', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>EBITDA: R$ %{y}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Receita x EBITDA (Últimos 12 Meses)", font=dict(size=18, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=400,
        legend=dict(font=dict(color='#FFFFFF')),
        xaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0'),
        yaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0', title='Valor (R$ Milhões)')
    )
    
    return fig

def criar_grafico_investimento_capex():
    """Gráfico de barras empilhadas Investimento vs Capex"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    investimento = [2.1, 1.8, 2.5, 2.2, 2.8, 3.1, 2.9, 3.2, 3.0, 3.5, 3.3, 3.8]
    capex = [1.2, 1.5, 1.8, 1.4, 2.1, 2.3, 2.0, 2.4, 2.2, 2.6, 2.5, 2.9]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses, y=investimento,
        name='Investimento',
        marker=dict(color='#C0C0C0'),
        hovertemplate='<b>%{x}</b><br>Investimento: R$ %{y}M<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=meses, y=capex,
        name='Capex',
        marker=dict(color='#FFD700'),
        hovertemplate='<b>%{x}</b><br>Capex: R$ %{y}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Investimento vs Capex por Mês", font=dict(size=18, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=400,
        barmode='stack',
        legend=dict(font=dict(color='#FFFFFF')),
        xaxis=dict(showgrid=False, color='#C0C0C0'),
        yaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0', title='Valor (R$ Milhões)')
    )
    
    return fig

# ============================================================================
# DASHBOARDS POR UNIDADE DE NEGÓCIO
# ============================================================================

def dashboard_fox_graos():
    """Dashboard específico da Fox Grãos"""
    
    st.markdown('<h2 style="color: #FFFFFF; border-bottom: 2px solid #90EE90; padding-bottom: 0.5rem;">🌾 Fox Grãos - Trade Triangular & Logística</h2>', unsafe_allow_html=True)
    
    # Trade Triangular
    st.markdown('<h3 style="color: #90EE90; margin: 2rem 0 1rem 0;">📈 Operação de Trade Triangular</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    trade_kpis = [
        {'label': 'Volume Negociado', 'value': '125.8k t', 'delta': 'Últimos 30 dias'},
        {'label': 'Receita Trade', 'value': 'R$ 89.2M', 'delta': '+18.5% vs mês anterior'},
        {'label': 'Margem de Trade', 'value': '12.8%', 'delta': '+2.1 p.p.'},
        {'label': 'Ciclo Médio', 'value': '18 dias', 'delta': '-3 dias vs média'}
    ]
    
    for i, kpi in enumerate(trade_kpis):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid #90EE90;
                text-align: center;
            ">
                <div style="color: #C0C0C0; font-size: 0.8rem;">{kpi['label']}</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{kpi['value']}</div>
                <div style="color: #90EE90; font-size: 0.8rem;">{kpi['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Logística
    st.markdown('<h3 style="color: #90EE90; margin: 2rem 0 1rem 0;">🚛 Logística</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume por tipo de grão
        fig_volume_graos = criar_grafico_volume_graos()
        st.plotly_chart(fig_volume_graos, use_container_width=True)
    
    with col2:
        # Linha do tempo de contratos
        fig_timeline_contratos = criar_timeline_contratos()
        st.plotly_chart(fig_timeline_contratos, use_container_width=True)

def dashboard_fox_log():
    """Dashboard específico da Fox Log"""
    
    st.markdown('<h2 style="color: #FFFFFF; border-bottom: 2px solid #FFD700; padding-bottom: 0.5rem;">🚛 Fox Log - Logística & Insumos</h2>', unsafe_allow_html=True)
    
    # Transporte e Armazenagem
    col1, col2, col3, col4 = st.columns(4)
    
    log_kpis = [
        {'label': 'Receita Transporte', 'value': 'R$ 45.8M', 'delta': '+12.3%'},
        {'label': 'Receita Armazenagem', 'value': 'R$ 18.2M', 'delta': '+8.7%'},
        {'label': 'Volume Transportado', 'value': '89.5k t', 'delta': '+15.2%'},
        {'label': 'SLA Pontualidade', 'value': '94.8%', 'delta': '+2.1 p.p.'}
    ]
    
    for i, kpi in enumerate(log_kpis):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid #FFD700;
                text-align: center;
            ">
                <div style="color: #C0C0C0; font-size: 0.8rem;">{kpi['label']}</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{kpi['value']}</div>
                <div style="color: #FFD700; font-size: 0.8rem;">{kpi['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Modalidades e Heatmap de custos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_modalidades = criar_grafico_modalidades()
        st.plotly_chart(fig_modalidades, use_container_width=True)
    
    with col2:
        fig_heatmap_custos = criar_heatmap_custos()
        st.plotly_chart(fig_heatmap_custos, use_container_width=True)

def dashboard_clube_fx():
    """Dashboard específico do Clube FX"""
    
    st.markdown('<h2 style="color: #FFFFFF; border-bottom: 2px solid #87CEEB; padding-bottom: 0.5rem;">💼 Clube FX - Consultoria</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    clube_kpis = [
        {'label': 'Clientes Atendidos', 'value': '247', 'delta': '+18 novos clientes'},
        {'label': 'Receita Consultoria', 'value': 'R$ 12.8M', 'delta': '+22.5%'},
        {'label': 'NPS Score', 'value': '8.7/10', 'delta': '+0.3 vs trimestre'},
        {'label': 'Taxa Retenção', 'value': '92.3%', 'delta': '+1.8 p.p.'}
    ]
    
    for i, kpi in enumerate(clube_kpis):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid #87CEEB;
                text-align: center;
            ">
                <div style="color: #C0C0C0; font-size: 0.8rem;">{kpi['label']}</div>
                <div style="color: #FFFFFF; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;">{kpi['value']}</div>
                <div style="color: #87CEEB; font-size: 0.8rem;">{kpi['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_receita_servicos = criar_grafico_receita_servicos()
        st.plotly_chart(fig_receita_servicos, use_container_width=True)
    
    with col2:
        # Lista de projetos em andamento
        st.markdown('<h4 style="color: #87CEEB;">Projetos em Andamento</h4>', unsafe_allow_html=True)
        
        projetos = [
            {'nome': 'Implementação DRE Fazenda Santa Maria', 'progresso': 85},
            {'nome': 'Consultoria DFC Agropecuária Boa Vista', 'progresso': 60},
            {'nome': 'Orçamento vs Realizado Cooperativa Central', 'progresso': 40},
            {'nome': 'Análise de Custos Fazenda Progresso', 'progresso': 95}
        ]
        
        for projeto in projetos:
            st.markdown(f'''
            <div style="margin: 1rem 0; padding: 1rem; background: #2d2d2d; border-radius: 8px;">
                <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">{projeto['nome']}</div>
                <div style="background: #1a1a1a; border-radius: 10px; height: 8px; overflow: hidden;">
                    <div style="background: #87CEEB; height: 100%; width: {projeto['progresso']}%; transition: width 0.3s;"></div>
                </div>
                <div style="color: #C0C0C0; font-size: 0.8rem; margin-top: 0.3rem;">{projeto['progresso']}% concluído</div>
            </div>
            ''', unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES AUXILIARES PARA GRÁFICOS
# ============================================================================

def criar_grafico_volume_graos():
    """Gráfico de volume por tipo de grão"""
    graos = ['Soja', 'Milho', 'Sorgo', 'Outros']
    volumes = [45.2, 32.8, 18.5, 12.1]
    
    fig = go.Figure(data=[go.Bar(
        x=graos, y=volumes,
        marker=dict(color=['#90EE90', '#FFD700', '#C0C0C0', '#87CEEB']),
        text=volumes,
        textposition='outside',
        texttemplate='%{text}k t'
    )])
    
    fig.update_layout(
        title="Volume por Tipo de Grão",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=350,
        yaxis=dict(title='Volume (mil toneladas)', color='#C0C0C0'),
        xaxis=dict(color='#C0C0C0')
    )
    
    return fig

def criar_timeline_contratos():
    """Timeline de principais contratos"""
    fig = go.Figure()
    
    datas = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
    contratos = [12, 8, 15, 10, 18, 14]
    
    fig.add_trace(go.Scatter(
        x=datas, y=contratos,
        mode='lines+markers',
        line=dict(color='#90EE90', width=3),
        marker=dict(size=10, color='#90EE90'),
        name='Contratos Fechados'
    ))
    
    fig.update_layout(
        title="Contratos Fechados por Mês",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=350,
        yaxis=dict(title='Número de Contratos', color='#C0C0C0'),
        xaxis=dict(color='#C0C0C0')
    )
    
    return fig

def criar_grafico_modalidades():
    """Gráfico de modalidades de contratação"""
    modalidades = ['Aluguel Caminhões', 'Transportadoras', 'Autônomos']
    valores = [45, 35, 20]
    
    fig = go.Figure(data=[go.Pie(
        labels=modalidades,
        values=valores,
        hole=0.4,
        marker=dict(colors=['#FFD700', '#C0C0C0', '#87CEEB'])
    )])
    
    fig.update_layout(
        title="Distribuição de Modalidades",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=350
    )
    
    return fig

def criar_heatmap_custos():
    """Heatmap de custos operacionais"""
    modalidades = ['Aluguel', 'Transportadoras', 'Autônomos']
    cargas = ['Soja', 'Milho', 'Sorgo', 'Insumos']
    
    custos = np.array([
        [120, 135, 145, 160],
        [110, 125, 140, 155],
        [105, 120, 135, 150]
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=custos,
        x=cargas,
        y=modalidades,
        colorscale='Greys',
        showscale=True
    ))
    
    fig.update_layout(
        title="Custo Operacional por Modalidade e Carga (R$/t)",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=350
    )
    
    return fig

def criar_grafico_receita_servicos():
    """Gráfico de receita por tipo de serviço"""
    servicos = ['DRE', 'DFC', 'Orçado vs Real', 'Outros']
    receitas = [4.2, 3.8, 2.9, 1.9]
    
    fig = go.Figure(data=[go.Bar(
        x=servicos, y=receitas,
        marker=dict(color='#87CEEB'),
        text=receitas,
        textposition='outside',
        texttemplate='R$ %{text}M'
    )])
    
    fig.update_layout(
        title="Receita por Tipo de Serviço",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=350,
        yaxis=dict(title='Receita (R$ Milhões)', color='#C0C0C0'),
        xaxis=dict(color='#C0C0C0')
    )
    
    return fig

# ============================================================================
# CSS PREMIUM
# ============================================================================

def aplicar_css_premium():
    """CSS premium para o dashboard"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #FFFFFF;
            font-family: 'Inter', sans-serif;
        }
        
        /* Esconder sidebar */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        /* Estilizar selectboxes */
        .stSelectbox > div > div {
            background: #2d2d2d !important;
            border: 1px solid #444444 !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
        }
        
        /* Estilizar botões */
        .stButton > button {
            background: linear-gradient(135deg, #333333 0%, #555555 100%) !important;
            border: 1px solid #666666 !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            border-color: #C0C0C0 !important;
            box-shadow: 0 0 10px rgba(192, 192, 192, 0.3) !important;
        }
        
        /* Estilizar checkboxes */
        .stCheckbox > label {
            color: #FFFFFF !important;
        }
        
        /* Estilizar date inputs */
        .stDateInput > div > div > input {
            background: #2d2d2d !important;
            border: 1px solid #444444 !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard"""
    configurar_pagina()
    aplicar_css_premium()
    
    # Inicializar session state
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
    
    # Mostrar tela de boas-vindas ou dashboard principal
    if st.session_state.show_welcome:
        filtros = tela_boas_vindas()
    else:
        # Menu de navegação no topo
        st.markdown('<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 2rem;">🌾 FOX SA - Painel de Resultados em Tempo Real</h1>', unsafe_allow_html=True)
        
        # Controles de navegação
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            opcao = st.selectbox(
                "📊 Selecionar Seção:",
                [
                    "Visão Consolidada",
                    "Fox Grãos - Trade & Logística", 
                    "Fox Log - Transporte & Insumos",
                    "Clube FX - Consultoria",
                    "Performance Financeira",
                    "DRE em Tempo Real",
                    "Insights & Tendências",
                    "Projeções & Cenários",
                    "Roadmap & Ações",
                    "Configurações"
                ],
                key="main_navigation"
            )
        
        with col2:
            periodo = st.selectbox(
                "📅 Período:",
                ["Últimos 12 meses", "Últimos 6 meses", "Último trimestre", "Personalizado"],
                key="periodo_select"
            )
        
        with col3:
            visualizacao = st.selectbox(
                "👁️ Visualização:",
                ["Executiva", "Detalhada", "Operacional"],
                key="view_select"
            )
        
        with col4:
            if st.button("🏠 Início", key="home_btn"):
                st.session_state.show_welcome = True
                st.rerun()
        
        st.markdown('<hr style="margin: 1.5rem 0; border: 1px solid #333333;">', unsafe_allow_html=True)
        
        # Carregar dados
        dados_eda = carregar_dados_eda()
        dados_financeiros = carregar_dados_financeiros()
        
        # Roteamento de páginas
        if opcao == "Visão Consolidada":
            visao_consolidada(dados_eda, dados_financeiros)
        
        elif opcao == "Fox Grãos - Trade & Logística":
            dashboard_fox_graos()
        
        elif opcao == "Fox Log - Transporte & Insumos":
            dashboard_fox_log()
        
        elif opcao == "Clube FX - Consultoria":
            dashboard_clube_fx()
        
        else:
            st.markdown(f'<h2 style="color: #FFFFFF;">🚧 {opcao}</h2>', unsafe_allow_html=True)
            st.info("Esta seção está em desenvolvimento. Em breve estará disponível!")

if __name__ == "__main__":
    main()

