#!/usr/bin/env python3
"""
Fox SA Investor Data-Room Dashboard
Versão completa com 4 verticais: Fox Grãos, Fox Log, Clube FX, GHX
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

def configurar_pagina():
    """Configuração inicial da página"""
    st.set_page_config(
        page_title="Fox SA Investor Data-Room",
        page_icon="🦊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ============================================================================
# SISTEMA DE IDIOMAS
# ============================================================================

def get_translations():
    """Dicionário de traduções PT-BR/EN"""
    return {
        'pt': {
            'title': 'Fox SA Investor Data-Room Dashboard',
            'home': 'Home / Visão Geral',
            'corporate': 'Societário & Governança',
            'financial': 'Financeiro Consolidado',
            'fox_graos': 'Fox Grãos',
            'fox_log': 'Fox Log',
            'clube_fx': 'Clube FX',
            'ghx': 'GHX - Insumos',
            'fiscal': 'Fiscal & Tributário',
            'legal': 'Legal & Compliance',
            'hr': 'Recursos Humanos',
            'tech': 'Tecnologia & Segurança',
            'esg': 'ESG & Riscos',
            'projections': 'Projeções 2025-2028',
            'qa': 'Q&A / Logs',
            'search_placeholder': 'Busca global...',
            'user_permissions': 'Usuário/Permissões',
            'revenue_ytd': 'Receita YTD',
            'ebitda_ytd': 'EBITDA YTD',
            'cash_vs_debt': 'Caixa vs. Dívida',
            'clube_fx_clients': 'Clientes Clube FX',
            'ghx_revenue': 'Receita GHX',
            'last_uploads': 'Últimos Uploads',
            'open_qa': 'Q&A Abertos',
            'compliance_note': 'Dados financeiros auditados quando marcado; projeções forward-looking.',
            'dark_mode': 'Modo Escuro',
            'language': 'Idioma'
        },
        'en': {
            'title': 'Fox SA Investor Data-Room Dashboard',
            'home': 'Home / Overview',
            'corporate': 'Corporate & Governance',
            'financial': 'Consolidated Financial',
            'fox_graos': 'Fox Grãos',
            'fox_log': 'Fox Log',
            'clube_fx': 'Clube FX',
            'ghx': 'GHX - Inputs',
            'fiscal': 'Tax & Fiscal',
            'legal': 'Legal & Compliance',
            'hr': 'Human Resources',
            'tech': 'Technology & Security',
            'esg': 'ESG & Risks',
            'projections': 'Projections 2025-2028',
            'qa': 'Q&A / Logs',
            'search_placeholder': 'Global search...',
            'user_permissions': 'User/Permissions',
            'revenue_ytd': 'Revenue YTD',
            'ebitda_ytd': 'EBITDA YTD',
            'cash_vs_debt': 'Cash vs. Debt',
            'clube_fx_clients': 'Clube FX Clients',
            'ghx_revenue': 'GHX Revenue',
            'last_uploads': 'Last Uploads',
            'open_qa': 'Open Q&A',
            'compliance_note': 'Audited financial data when marked; forward-looking projections.',
            'dark_mode': 'Dark Mode',
            'language': 'Language'
        }
    }

def get_text(key, lang='pt'):
    """Obter texto traduzido"""
    translations = get_translations()
    return translations.get(lang, translations['pt']).get(key, key)

# ============================================================================
# DADOS SIMULADOS
# ============================================================================

def get_kpi_data():
    """Dados dos KPIs principais"""
    return {
        'receita_ytd': 247000000,  # R$ 247M
        'ebitda_ytd': 9880000,     # R$ 9.88M (4%)
        'ebitda_margin': 4.0,      # 4%
        'caixa': 45000000,         # R$ 45M
        'divida': 23000000,        # R$ 23M
        'clientes_clube_fx': 1247,
        'receita_ghx': 18500000    # R$ 18.5M
    }

def get_vertical_data():
    """Dados das 4 verticais para heat-map"""
    return {
        'Fox Grãos': {
            'receita': 156000000,  # R$ 156M
            'participacao': 63.2,  # 63.2%
            'crescimento': 18.5,   # +18.5% YoY
            'margem': 3.8          # 3.8%
        },
        'Fox Log': {
            'receita': 52000000,   # R$ 52M
            'participacao': 21.1,  # 21.1%
            'crescimento': 24.3,   # +24.3% YoY
            'margem': 4.2          # 4.2%
        },
        'Clube FX': {
            'receita': 20500000,   # R$ 20.5M
            'participacao': 8.3,   # 8.3%
            'crescimento': 45.7,   # +45.7% YoY
            'margem': 5.1          # 5.1%
        },
        'GHX': {
            'receita': 18500000,   # R$ 18.5M
            'participacao': 7.4,   # 7.4%
            'crescimento': 67.2,   # +67.2% YoY (nova vertical)
            'margem': 4.5          # 4.5%
        }
    }

def get_projections_data():
    """Dados das projeções 2025-2028 incluindo GHX"""
    return {
        'anos': [2025, 2026, 2027, 2028],
        'receita_total': [160, 295, 543, 1000],  # R$ milhões
        'fox_graos': [95, 165, 295, 520],        # R$ milhões
        'fox_log': [35, 70, 135, 260],           # R$ milhões
        'clube_fx': [18, 35, 68, 130],           # R$ milhões
        'ghx': [12, 25, 45, 90],                 # R$ milhões
        'ebitda_percent': [4.0, 4.0, 4.0, 4.0], # 4% constante
        'ebitda_valor': [6.4, 11.8, 21.7, 40.0] # R$ milhões
    }

# ============================================================================
# BARRA FIXA SUPERIOR
# ============================================================================

def criar_barra_fixa():
    """Cria barra fixa superior com logo, busca e usuário"""
    
    # CSS para barra fixa
    st.markdown("""
    <style>
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
        z-index: 1000;
        display: flex;
        align-items: center;
        padding: 0 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-content {
        margin-top: 70px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        color: white;
        font-size: 20px;
        font-weight: bold;
    }
    
    .search-section {
        flex: 1;
        margin: 0 20px;
    }
    
    .user-section {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Barra fixa
    st.markdown("""
    <div class="top-bar">
        <div class="logo-section">
            🦊 Fox SA Data-Room
        </div>
        <div class="search-section">
            <!-- Busca global será implementada aqui -->
        </div>
        <div class="user-section">
            👤 Investidor
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SEÇÕES DO DASHBOARD
# ============================================================================

def secao_home(lang='pt'):
    """Seção 1: Home / Visão Geral"""
    st.markdown(f'<div class="main-content">', unsafe_allow_html=True)
    st.markdown(f'<h1>🏠 {get_text("home", lang)}</h1>', unsafe_allow_html=True)
    
    # KPI Cards
    kpis = get_kpi_data()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            get_text("revenue_ytd", lang),
            f"R$ {kpis['receita_ytd']/1000000:.0f}M",
            delta="+18.5%"
        )
    
    with col2:
        st.metric(
            get_text("ebitda_ytd", lang),
            f"R$ {kpis['ebitda_ytd']/1000000:.1f}M",
            delta=f"{kpis['ebitda_margin']:.1f}%"
        )
    
    with col3:
        st.metric(
            get_text("cash_vs_debt", lang),
            f"R$ {(kpis['caixa']-kpis['divida'])/1000000:.0f}M",
            delta="Caixa líquido positivo"
        )
    
    with col4:
        st.metric(
            get_text("clube_fx_clients", lang),
            f"{kpis['clientes_clube_fx']:,}",
            delta="+247 novos"
        )
    
    with col5:
        st.metric(
            get_text("ghx_revenue", lang),
            f"R$ {kpis['receita_ghx']/1000000:.1f}M",
            delta="+67.2% YoY"
        )
    
    # Heat-map das 4 verticais
    st.markdown("### 📊 Participação por Vertical")
    
    verticais = get_vertical_data()
    
    # Criar gráfico de pizza
    labels = list(verticais.keys())
    values = [v['participacao'] for v in verticais.values()]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Distribuição de Receita por Vertical",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Últimos uploads e Q&A
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📁 Últimos Uploads")
        st.markdown("""
        - **Balanço Q3 2024** - Auditado (2 dias atrás)
        - **Contrato Cargill** - Fox Grãos (5 dias atrás)
        - **Relatório ESG** - Sustentabilidade (1 semana atrás)
        """)
    
    with col2:
        st.markdown("### ❓ Q&A Abertos")
        st.markdown("""
        - **Projeção GHX 2025** - Aguardando resposta
        - **Margem Fox Log** - Em análise
        - **Plano de expansão** - Respondido
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def secao_ghx(lang='pt'):
    """Seção 7: GHX - Venda Direta de Insumos"""
    st.markdown(f'<h1>🌱 {get_text("ghx", lang)}</h1>', unsafe_allow_html=True)
    
    # Métricas GHX
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Receita GHX YTD", "R$ 18.5M", delta="+67.2% YoY")
    
    with col2:
        st.metric("Produtos Ativos", "1,247", delta="+89 novos")
    
    with col3:
        st.metric("Margem Média", "4.5%", delta="+0.3pp")
    
    with col4:
        st.metric("Clientes Ativos", "342", delta="+78 novos")
    
    # Gráfico de vendas por categoria
    st.markdown("### 📊 Vendas por Categoria de Insumo")
    
    categorias = ['Fertilizantes', 'Defensivos', 'Sementes', 'Nutrição Animal', 'Outros']
    vendas = [7.2, 5.8, 3.1, 1.8, 0.6]  # R$ milhões
    margens = [4.2, 5.1, 4.8, 3.9, 4.5]  # %
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Vendas (R$ M)',
        x=categorias,
        y=vendas,
        marker_color='#96CEB4',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        name='Margem (%)',
        x=categorias,
        y=margens,
        mode='lines+markers',
        marker_color='#FF6B6B',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Vendas e Margem por Categoria',
        xaxis_title='Categoria',
        yaxis=dict(title='Vendas (R$ M)', side='left'),
        yaxis2=dict(title='Margem (%)', side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de clientes (simulado)
    st.markdown("### 🗺️ Distribuição de Clientes GHX")
    
    # Dados simulados de clientes por estado
    estados_data = {
        'Estado': ['GO', 'MT', 'MS', 'MG', 'SP', 'PR', 'RS'],
        'Clientes': [89, 67, 45, 52, 38, 31, 20],
        'Receita': [5.2, 4.1, 2.8, 3.1, 2.0, 1.1, 0.2]
    }
    
    df_estados = pd.DataFrame(estados_data)
    
    fig = px.bar(df_estados, x='Estado', y='Receita', 
                 title='Receita GHX por Estado (R$ M)',
                 color='Receita',
                 color_continuous_scale='Greens')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Principais fornecedores
    st.markdown("### 🤝 Principais Parcerias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Fornecedores Estratégicos:**
        - Yara Brasil (Fertilizantes)
        - Bayer CropScience (Defensivos)
        - Syngenta (Sementes)
        - Cargill (Nutrição Animal)
        """)
    
    with col2:
        st.markdown("""
        **Contratos Principais:**
        - [📄 Acordo Yara 2024-2026](link)
        - [📄 Parceria Bayer](link)
        - [📄 Distribuição Syngenta](link)
        - [📄 Fornecimento Cargill](link)
        """)

def secao_projections_com_ghx(lang='pt'):
    """Seção 13: Projeções 2025-2028 incluindo GHX"""
    st.markdown(f'<h1>📈 {get_text("projections", lang)}</h1>', unsafe_allow_html=True)
    
    # Card de meta 2028
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
        <h2>🎯 Meta 2028: R$ 1 bilhão | EBITDA 4% (R$ 40 milhões)</h2>
        <p>Crescimento sustentável com 4 verticais integradas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dados das projeções
    proj = get_projections_data()
    
    # Gráfico de barras empilhadas com linha EBITDA
    fig = go.Figure()
    
    # Barras empilhadas por vertical
    fig.add_trace(go.Bar(
        name='Fox Grãos',
        x=proj['anos'],
        y=proj['fox_graos'],
        marker_color='#FF6B6B'
    ))
    
    fig.add_trace(go.Bar(
        name='Fox Log',
        x=proj['anos'],
        y=proj['fox_log'],
        marker_color='#4ECDC4'
    ))
    
    fig.add_trace(go.Bar(
        name='Clube FX',
        x=proj['anos'],
        y=proj['clube_fx'],
        marker_color='#45B7D1'
    ))
    
    fig.add_trace(go.Bar(
        name='GHX',
        x=proj['anos'],
        y=proj['ghx'],
        marker_color='#96CEB4'
    ))
    
    # Linha EBITDA
    fig.add_trace(go.Scatter(
        name='EBITDA (R$ M)',
        x=proj['anos'],
        y=proj['ebitda_valor'],
        mode='lines+markers',
        marker_color='#FFD700',
        line=dict(width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Projeções de Receita por Vertical + EBITDA',
        xaxis_title='Ano',
        yaxis=dict(title='Receita (R$ M)', side='left'),
        yaxis2=dict(title='EBITDA (R$ M)', side='right', overlaying='y'),
        barmode='stack',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de projeções
    st.markdown("### 📊 Tabela de Projeções")
    
    df_proj = pd.DataFrame({
        'Ano': proj['anos'],
        'Receita (R$ mi)': proj['receita_total'],
        '% YoY': ['—', '84%', '84%', '84%'],
        'EBITDA %': [f"{x:.0f}%" for x in proj['ebitda_percent']],
        'EBITDA R$ mi': proj['ebitda_valor']
    })
    
    # Destacar 2025E e 2028E
    def highlight_years(row):
        if row['Ano'] in [2025, 2028]:
            return ['background-color: #FFE4B5'] * len(row)
        return [''] * len(row)
    
    st.dataframe(df_proj.style.apply(highlight_years, axis=1), use_container_width=True)
    
    # Aba de premissas
    with st.expander("🔧 Premissas e Drivers"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Drivers de Crescimento:**
            - CAGR Grãos: 75% (expansão geográfica)
            - CAGR Log: 85% (novos contratos)
            - CAGR Clube FX: 95% (digitalização)
            - CAGR GHX: 100% (nova vertical)
            """)
        
        with col2:
            st.markdown("""
            **Premissas Operacionais:**
            - Margem EBITDA: 4% constante
            - Preço saca: R$ 85-95
            - Churn Clube FX: <5%
            - Penetração GHX: 15% do mercado regional
            """)

# ============================================================================
# NAVEGAÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do data-room"""
    configurar_pagina()
    
    # Inicializar session state
    if 'language' not in st.session_state:
        st.session_state.language = 'pt'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Barra fixa superior
    criar_barra_fixa()
    
    # Sidebar com navegação
    with st.sidebar:
        st.markdown("### 🦊 Fox SA Data-Room")
        
        # Seletor de idioma
        lang_options = {'Português': 'pt', 'English': 'en'}
        lang_display = st.selectbox(
            get_text('language', st.session_state.language),
            options=list(lang_options.keys()),
            index=0 if st.session_state.language == 'pt' else 1
        )
        st.session_state.language = lang_options[lang_display]
        
        # Modo escuro
        st.session_state.dark_mode = st.checkbox(
            get_text('dark_mode', st.session_state.language),
            value=st.session_state.dark_mode
        )
        
        st.markdown("---")
        
        # Menu de navegação
        opcoes_menu = [
            get_text('home', st.session_state.language),
            get_text('corporate', st.session_state.language),
            get_text('financial', st.session_state.language),
            get_text('fox_graos', st.session_state.language),
            get_text('fox_log', st.session_state.language),
            get_text('clube_fx', st.session_state.language),
            get_text('ghx', st.session_state.language),
            get_text('fiscal', st.session_state.language),
            get_text('legal', st.session_state.language),
            get_text('hr', st.session_state.language),
            get_text('tech', st.session_state.language),
            get_text('esg', st.session_state.language),
            get_text('projections', st.session_state.language),
            get_text('qa', st.session_state.language)
        ]
        
        opcao_selecionada = st.selectbox(
            "📋 Seções",
            opcoes_menu,
            index=0
        )
    
    # Roteamento das seções
    if opcao_selecionada == get_text('home', st.session_state.language):
        secao_home(st.session_state.language)
    elif opcao_selecionada == get_text('corporate', st.session_state.language):
        secao_societario(st.session_state.language)
    elif opcao_selecionada == get_text('financial', st.session_state.language):
        secao_financeiro(st.session_state.language)
    elif opcao_selecionada == get_text('fox_graos', st.session_state.language):
        secao_fox_graos(st.session_state.language)
    elif opcao_selecionada == get_text('fox_log', st.session_state.language):
        secao_fox_log(st.session_state.language)
    elif opcao_selecionada == get_text('clube_fx', st.session_state.language):
        secao_clube_fx(st.session_state.language)
    elif opcao_selecionada == get_text('ghx', st.session_state.language):
        secao_ghx(st.session_state.language)
    elif opcao_selecionada == get_text('projections', st.session_state.language):
        secao_projections_com_ghx(st.session_state.language)
    else:
        st.markdown(f'<div class="main-content">', unsafe_allow_html=True)
        st.markdown(f'<h1>🚧 {opcao_selecionada}</h1>', unsafe_allow_html=True)
        st.info("Seção em desenvolvimento. Será implementada nas próximas fases.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Nota de compliance
    st.markdown("---")
    st.markdown(f"ℹ️ {get_text('compliance_note', st.session_state.language)}")

if __name__ == "__main__":
    main()



# ============================================================================
# SEÇÕES 2-6: IMPLEMENTAÇÃO COMPLETA
# ============================================================================

def secao_societario(lang='pt'):
    """Seção 2: Societário & Governança"""
    st.markdown(f'<h1>🏛️ {get_text("corporate", lang)}</h1>', unsafe_allow_html=True)
    
    # Cap-table interativo
    st.markdown("### 📊 Estrutura Societária")
    
    # Dados do cap-table
    cap_table_data = {
        'Sócio': ['Fundadores', 'Família Silva', 'Investidor Anjo', 'Funcionários (Stock Options)', 'Reserva Futura'],
        'Participação (%)': [45.0, 25.0, 15.0, 10.0, 5.0],
        'Tipo': ['Ordinárias', 'Ordinárias', 'Preferenciais', 'Stock Options', 'Reserva'],
        'Valor Investido (R$)': [0, 0, 2500000, 0, 0],
        'Data Entrada': ['2019-01', '2019-01', '2022-06', '2023-01', '-']
    }
    
    df_cap = pd.DataFrame(cap_table_data)
    
    # Gráfico de pizza do cap-table
    fig = go.Figure(data=[go.Pie(
        labels=df_cap['Sócio'],
        values=df_cap['Participação (%)'],
        hole=0.4,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA07A'],
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Distribuição Societária Atual",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.dataframe(df_cap, use_container_width=True)
    
    # Árvore societária
    st.markdown("### 🌳 Estrutura Corporativa")
    
    st.markdown("""
    ```
    Fox SA Holding
    ├── Fox Grãos Ltda (100%)
    │   ├── Fox Originação (100%)
    │   └── Fox Trading (100%)
    ├── Fox Logística Ltda (100%)
    │   ├── Fox Transporte (100%)
    │   └── Fox Armazenagem (80%)
    ├── Clube FX Tecnologia Ltda (100%)
    │   └── Clube FX Serviços (100%)
    └── GHX Insumos Ltda (100%)
        ├── GHX Distribuição (100%)
        └── GHX Varejo (60%)
    ```
    """)
    
    # Documentos societários
    st.markdown("### 📄 Documentos Societários")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Atas e Deliberações:**
        - [📄 Ata AGO 2024](link) - Aprovação das demonstrações
        - [📄 Ata AGE 2024](link) - Aumento de capital
        - [📄 Ata Conselho 2024](link) - Nomeação diretores
        - [📄 Procurações](link) - Poderes de representação
        """)
    
    with col2:
        st.markdown("""
        **Contratos Societários:**
        - [📄 Contrato Social Atual](link) - Consolidado 2024
        - [📄 Acordo de Acionistas](link) - Tag along, drag along
        - [📄 Stock Option Plan](link) - Plano de opções
        - [📄 Política de Dividendos](link) - Distribuição de resultados
        """)

def secao_financeiro(lang='pt'):
    """Seção 3: Financeiro Consolidado"""
    st.markdown(f'<h1>💰 {get_text("financial", lang)}</h1>', unsafe_allow_html=True)
    
    # Seletor de período
    col1, col2, col3 = st.columns(3)
    
    with col1:
        periodo = st.selectbox("Período", ["2024 YTD", "2023 Anual", "2022 Anual", "2021 Anual"])
    
    with col2:
        demonstracao = st.selectbox("Demonstração", ["DRE", "Balanço Patrimonial", "DFC"])
    
    with col3:
        formato = st.selectbox("Formato", ["Consolidado", "Por Vertical", "Trimestral"])
    
    # DRE Consolidada
    if demonstracao == "DRE":
        st.markdown("### 📊 Demonstração do Resultado do Exercício")
        
        # Dados da DRE
        dre_data = {
            'Conta': [
                'Receita Bruta',
                '(-) Impostos sobre Vendas',
                'Receita Líquida',
                '(-) CPV',
                'Lucro Bruto',
                '(-) Despesas Operacionais',
                '  Despesas Comerciais',
                '  Despesas Administrativas',
                '  Outras Despesas',
                'EBITDA',
                '(-) Depreciação',
                'EBIT',
                '(-) Resultado Financeiro',
                'Lucro Antes do IR',
                '(-) IR/CSLL',
                'Lucro Líquido'
            ],
            '2024 YTD': [
                247000, -19760, 227240, -182000, 45240,
                -35360, -18200, -12480, -4680, 9880,
                -2470, 7410, -1850, 5560, -1390, 4170
            ],
            '2023': [
                189000, -15120, 173880, -139000, 34880,
                -27020, -13900, -9540, -3580, 7860,
                -1890, 5970, -1490, 4480, -1120, 3360
            ],
            '% Receita 2024': [
                100.0, -8.0, 92.0, -73.7, 18.3,
                -14.3, -7.4, -5.1, -1.9, 4.0,
                -1.0, 3.0, -0.7, 2.3, -0.6, 1.7
            ]
        }
        
        df_dre = pd.DataFrame(dre_data)
        
        # Formatação da tabela
        def format_currency(val):
            if isinstance(val, (int, float)):
                return f"R$ {val:,.0f}".replace(',', '.')
            return val
        
        df_dre_formatted = df_dre.copy()
        df_dre_formatted['2024 YTD'] = df_dre_formatted['2024 YTD'].apply(format_currency)
        df_dre_formatted['2023'] = df_dre_formatted['2023'].apply(format_currency)
        df_dre_formatted['% Receita 2024'] = df_dre_formatted['% Receita 2024'].apply(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
        
        st.dataframe(df_dre_formatted, use_container_width=True)
        
        # Gráfico de evolução trimestral
        st.markdown("### 📈 Evolução Trimestral")
        
        trimestres = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024', 'Q2 2024', 'Q3 2024']
        receita_trim = [42, 45, 48, 54, 58, 62, 67]
        ebitda_trim = [1.7, 1.9, 2.1, 2.2, 2.4, 2.6, 2.8]
        margem_trim = [4.0, 4.2, 4.4, 4.1, 4.1, 4.2, 4.2]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Receita (R$ M)',
            x=trimestres,
            y=receita_trim,
            marker_color='#4ECDC4',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            name='EBITDA (R$ M)',
            x=trimestres,
            y=ebitda_trim,
            mode='lines+markers',
            marker_color='#FF6B6B',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            name='Margem EBITDA (%)',
            x=trimestres,
            y=margem_trim,
            mode='lines+markers',
            marker_color='#FFD700',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Evolução Trimestral - Receita, EBITDA e Margem',
            xaxis_title='Trimestre',
            yaxis=dict(title='Valores (R$ M)', side='left'),
            yaxis2=dict(title='Margem (%)', side='right', overlaying='y'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Botão para PDF auditado
    st.markdown("### 📄 Documentos Auditados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 DRE Auditada 2023"):
            st.success("Download iniciado: DRE_Fox_SA_2023_Auditada.pdf")
    
    with col2:
        if st.button("📄 Balanço Auditado 2023"):
            st.success("Download iniciado: BP_Fox_SA_2023_Auditado.pdf")
    
    with col3:
        if st.button("📄 DFC Auditado 2023"):
            st.success("Download iniciado: DFC_Fox_SA_2023_Auditado.pdf")

def secao_fox_graos(lang='pt'):
    """Seção 4: Fox Grãos"""
    st.markdown(f'<h1>🌾 {get_text("fox_graos", lang)}</h1>', unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Volume Comercializado", "2.1M sacas", delta="+18.5% YoY")
    
    with col2:
        st.metric("Receita YTD", "R$ 156M", delta="+22.3% YoY")
    
    with col3:
        st.metric("Preço Médio", "R$ 74.28/saca", delta="+3.2% vs mercado")
    
    with col4:
        st.metric("Margem Bruta", "3.8%", delta="+0.5pp")
    
    # Gráfico de volumes
    st.markdown("### 📊 Volumes Mensais (Sacas)")
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov']
    compras = [180, 195, 220, 240, 280, 320, 350, 380, 290, 250, 200]
    vendas = [160, 180, 200, 225, 260, 300, 330, 360, 275, 235, 190]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Compras',
        x=meses,
        y=compras,
        marker_color='#96CEB4'
    ))
    
    fig.add_trace(go.Bar(
        name='Vendas',
        x=meses,
        y=vendas,
        marker_color='#FF6B6B'
    ))
    
    fig.update_layout(
        title='Volumes de Compra e Venda (Milhares de Sacas)',
        xaxis_title='Mês',
        yaxis_title='Volume (mil sacas)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de originação
    st.markdown("### 🗺️ Mapa de Originação")
    
    # Dados por região
    regioes_data = {
        'Região': ['Sudoeste GO', 'Sul GO', 'Norte MT', 'Leste MS', 'Triângulo MG'],
        'Volume (mil sacas)': [850, 620, 380, 180, 120],
        'Produtores': [145, 98, 67, 34, 28],
        'Preço Médio (R$)': [73.50, 74.20, 75.10, 73.80, 74.90]
    }
    
    df_regioes = pd.DataFrame(regioes_data)
    
    fig = px.bar(df_regioes, x='Região', y='Volume (mil sacas)',
                 title='Volume de Originação por Região',
                 color='Volume (mil sacas)',
                 color_continuous_scale='Greens')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Contratos principais
    st.markdown("### 📄 Principais Contratos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Contratos de Compra:**
        - [📄 Fazenda Santa Rita - 50k sacas](link)
        - [📄 Cooperativa Regional - 80k sacas](link)
        - [📄 Grupo Agropecuário - 120k sacas](link)
        """)
    
    with col2:
        st.markdown("""
        **Contratos de Venda:**
        - [📄 Cargill - 200k sacas](link)
        - [📄 ADM - 150k sacas](link)
        - [📄 Bunge - 180k sacas](link)
        """)

def secao_fox_log(lang='pt'):
    """Seção 5: Fox Log"""
    st.markdown(f'<h1>🚛 {get_text("fox_log", lang)}</h1>', unsafe_allow_html=True)
    
    # Métricas operacionais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("OTIF (On Time In Full)", "94.2%", delta="+2.1pp")
    
    with col2:
        st.metric("Custo por KM", "R$ 3.85", delta="-R$ 0.12")
    
    with col3:
        st.metric("KM Rodados YTD", "1.2M km", delta="+28.5%")
    
    with col4:
        st.metric("Receita YTD", "R$ 52M", delta="+24.3%")
    
    # Gauge OTIF
    st.markdown("### 🎯 Indicador OTIF")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = 94.2,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "OTIF (%)"},
        delta = {'reference': 92.1},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#4ECDC4"},
            'steps': [
                {'range': [0, 80], 'color': "#FFE4E1"},
                {'range': [80, 90], 'color': "#FFFACD"},
                {'range': [90, 100], 'color': "#F0FFF0"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de rotas
    st.markdown("### 🗺️ Principais Rotas")
    
    rotas_data = {
        'Rota': ['GO → SP', 'MT → SP', 'MS → SP', 'GO → RJ', 'MT → PR'],
        'Distância (km)': [920, 1150, 1080, 1200, 680],
        'Frequência/mês': [45, 32, 28, 18, 25],
        'Custo/km (R$)': [3.75, 4.10, 3.95, 4.25, 3.60]
    }
    
    df_rotas = pd.DataFrame(rotas_data)
    
    fig = px.scatter(df_rotas, x='Distância (km)', y='Frequência/mês',
                     size='Custo/km (R$)', color='Rota',
                     title='Análise de Rotas: Distância vs Frequência')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # SLA por transportadora
    st.markdown("### 📊 Performance por Transportadora")
    
    transportadoras = ['Fox Log Própria', 'Parceiro A', 'Parceiro B', 'Parceiro C']
    otif_transp = [96.5, 93.2, 91.8, 89.4]
    custo_transp = [3.65, 3.85, 4.10, 4.25]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='OTIF (%)',
        x=transportadoras,
        y=otif_transp,
        marker_color='#4ECDC4',
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        name='Custo/km (R$)',
        x=transportadoras,
        y=custo_transp,
        mode='lines+markers',
        marker_color='#FF6B6B',
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='OTIF vs Custo por Transportadora',
        xaxis_title='Transportadora',
        yaxis=dict(title='OTIF (%)', side='left'),
        yaxis2=dict(title='Custo/km (R$)', side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def secao_clube_fx(lang='pt'):
    """Seção 6: Clube FX"""
    st.markdown(f'<h1>💳 {get_text("clube_fx", lang)}</h1>', unsafe_allow_html=True)
    
    # Métricas de clientes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Clientes Ativos", "1,247", delta="+247 novos")
    
    with col2:
        st.metric("Churn Rate 12m", "4.2%", delta="-1.3pp")
    
    with col3:
        st.metric("LTV/CAC", "3.8x", delta="+0.5x")
    
    with col4:
        st.metric("Receita YTD", "R$ 20.5M", delta="+45.7%")
    
    # Cohort chart de retenção
    st.markdown("### 📊 Análise de Cohort - Retenção de Clientes")
    
    # Dados simulados de cohort
    cohort_data = np.array([
        [100, 85, 78, 72, 68, 65],  # Cohort Jan
        [100, 87, 80, 75, 71, 68],  # Cohort Fev
        [100, 89, 82, 77, 73, 70],  # Cohort Mar
        [100, 88, 81, 76, 72, 69],  # Cohort Abr
        [100, 90, 83, 78, 74, 0],   # Cohort Mai
        [100, 91, 84, 79, 0, 0]     # Cohort Jun
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=cohort_data,
        x=['Mês 0', 'Mês 1', 'Mês 2', 'Mês 3', 'Mês 4', 'Mês 5'],
        y=['Jan 2024', 'Fev 2024', 'Mar 2024', 'Abr 2024', 'Mai 2024', 'Jun 2024'],
        colorscale='RdYlGn',
        text=cohort_data,
        texttemplate="%{text}%",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title='Cohort de Retenção (%)',
        xaxis_title='Período após Aquisição',
        yaxis_title='Cohort de Aquisição',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de churn
    st.markdown("### 📉 Análise de Churn")
    
    periodos = ['3 meses', '6 meses', '12 meses']
    churn_rates = [2.1, 3.2, 4.2]
    benchmark = [3.5, 5.2, 7.8]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Clube FX',
        x=periodos,
        y=churn_rates,
        marker_color='#4ECDC4'
    ))
    
    fig.add_trace(go.Bar(
        name='Benchmark Mercado',
        x=periodos,
        y=benchmark,
        marker_color='#FFB6C1'
    ))
    
    fig.update_layout(
        title='Churn Rate vs Benchmark de Mercado (%)',
        xaxis_title='Período',
        yaxis_title='Churn Rate (%)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Contratos principais
    st.markdown("### 📄 Contratos Principais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Parcerias Estratégicas:**
        - [📄 Banco Parceiro - Crédito Rural](link)
        - [📄 Seguradora - Seguro Agrícola](link)
        - [📄 Fintech - Pagamentos](link)
        """)
    
    with col2:
        st.markdown("""
        **Contratos Corporativos:**
        - [📄 Cooperativa Central - 500 produtores](link)
        - [📄 Sindicato Rural - 300 associados](link)
        - [📄 Grupo Agro - 150 fazendas](link)
        """)

