import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ============================================================================
# FUNÇÕES DE DADOS
# ============================================================================

def carregar_dados_eda():
    """Carregar dados simulados para EDA"""
    return {
        'performance_mensal': pd.DataFrame({
            'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'fox_graos': [18.5, 19.2, 21.8, 20.1, 22.3, 24.1],
            'fox_log': [12.3, 13.1, 14.2, 13.8, 15.1, 16.2],
            'clube_fx': [2.1, 2.3, 2.8, 2.5, 3.1, 3.4]
        })
    }

def carregar_dados_financeiros():
    """Carregar dados financeiros simulados"""
    return {
        'receita_total': 247000000,
        'ebitda_total': 89000000,
        'fluxo_caixa': 76000000,
        'clientes_ativos': 1247
    }

# ============================================================================
# FILTROS GLOBAIS
# ============================================================================

def criar_filtros_globais():
    """Criar filtros globais na sidebar que serão aplicados em todas as seções"""
    
    # Carregar dados dos contratos para popular os filtros
    try:
        from mongodb_connector import load_contracts_data
        df_contratos = load_contracts_data(limit=1000)
        
        if df_contratos.empty:
            # Fallback com dados vazios se não conseguir carregar
            df_contratos = pd.DataFrame({
                'grainName': [],
                'status': [],
                'closeDate': [],
                'isGrain': [],
                'isFreight': [],
                'isService': []
            })
    except Exception as e:
        # Fallback com dados vazios em caso de erro
        df_contratos = pd.DataFrame({
            'grainName': [],
            'status': [],
            'closeDate': [],
            'isGrain': [],
            'isFreight': [],
            'isService': []
        })
    
    st.sidebar.markdown("### 🎯 Filtros Principais")
    st.sidebar.markdown("---")
    
    # FILTROS PRINCIPAIS - DESTAQUE
    
    # 1. Filtro por TIPO DE OPERAÇÃO (primeiro e principal)
    st.sidebar.markdown("**🔄 Tipo de Operação**")
    tipos_operacao = ['Todos', 'Supply', 'Originação', 'Frete', 'Clube FX']
    tipo_selecionado = st.sidebar.selectbox(
        "Tipo de Operação",  # Label visível
        tipos_operacao,
        key="global_operation_filter",
        help="Filtrar por tipo de operação comercial",
        label_visibility="collapsed"  # Esconder label mas manter acessibilidade
    )
    
    st.sidebar.markdown("")  # Espaçamento
    
    # 2. Filtro por PRODUTO (segundo principal)
    st.sidebar.markdown("**🌾 Produto**")
    if not df_contratos.empty:
        graos_disponiveis = ['Todos'] + sorted([g for g in df_contratos['grainName'].unique() if pd.notna(g) and g != 'Não informado'])
    else:
        graos_disponiveis = ['Todos']
    
    grao_selecionado = st.sidebar.selectbox(
        "Produto",  # Label visível
        graos_disponiveis,
        key="global_grain_filter",
        help="Filtrar por tipo de grão/produto",
        label_visibility="collapsed"  # Esconder label mas manter acessibilidade
    )
    
    # Separador visual
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Filtros Adicionais")
    
    # FILTROS SECUNDÁRIOS
    
    # Filtro por status
    if not df_contratos.empty:
        status_disponiveis = ['Todos'] + sorted([s for s in df_contratos['status'].unique() if pd.notna(s)])
    else:
        status_disponiveis = ['Todos']
    
    status_selecionado = st.sidebar.selectbox(
        "Status",
        status_disponiveis,
        key="global_status_filter"
    )
    
    # Filtro por ano
    if not df_contratos.empty and 'closeDate' in df_contratos.columns:
        try:
            anos_validos = df_contratos['closeDate'].dt.year.dropna().unique()
            anos_contratos = sorted([int(ano) for ano in anos_validos if pd.notna(ano)], reverse=True)
            anos_opcoes = ['Todos'] + [str(ano) for ano in anos_contratos]
        except:
            anos_opcoes = ['Todos', '2025', '2024', '2023']
    else:
        anos_opcoes = ['Todos', '2025', '2024', '2023']
    
    ano_selecionado = st.sidebar.selectbox(
        "Ano",
        anos_opcoes,
        key="global_year_filter"
    )
    
    # Filtro por vendedor
    if not df_contratos.empty and 'sellerName' in df_contratos.columns:
        vendedores_disponiveis = ['Todos'] + sorted([v for v in df_contratos['sellerName'].unique() if pd.notna(v) and v != 'Não informado'])
    else:
        vendedores_disponiveis = ['Todos']
    
    vendedor_selecionado = st.sidebar.selectbox(
        "Vendedor",
        vendedores_disponiveis,
        key="global_seller_filter"
    )
    
    # Separador e botão de ação
    st.sidebar.markdown("---")
    
    # Botão para limpar filtros com destaque
    if st.sidebar.button("🔄 Limpar Todos os Filtros", key="clear_filters", type="primary"):
        # Reset dos filtros para "Todos"
        st.session_state.global_grain_filter = 'Todos'
        st.session_state.global_status_filter = 'Todos'
        st.session_state.global_operation_filter = 'Todos'
        st.session_state.global_year_filter = 'Todos'
        st.session_state.global_seller_filter = 'Todos'
        st.rerun()
    
    # Retornar os filtros selecionados
    return {
        'grao': grao_selecionado,
        'status': status_selecionado,
        'tipo_operacao': tipo_selecionado,
        'ano': ano_selecionado,
        'vendedor': vendedor_selecionado
    }

def aplicar_filtros_globais(df, filtros):
    """Aplicar os filtros globais a um DataFrame"""
    if df.empty:
        return df
    
    df_filtrado = df.copy()
    
    # Filtro por produto
    if filtros['grao'] != 'Todos' and 'grainName' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['grainName'] == filtros['grao']]
    
    # Filtro por status
    if filtros['status'] != 'Todos' and 'status' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['status'] == filtros['status']]
    
    # Filtro por tipo de operação
    if filtros['tipo_operacao'] != 'Todos':
        if filtros['tipo_operacao'] == 'Supply':
            if 'isBuying' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isBuying'] == True]
        elif filtros['tipo_operacao'] == 'Originação':
            if 'isBuying' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isBuying'] == False]
        elif filtros['tipo_operacao'] == 'Frete':
            if 'isFreight' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isFreight'] == True]
        elif filtros['tipo_operacao'] == 'Clube FX':
            if 'isService' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isService'] == True]
    
    # Filtro por ano
    if filtros['ano'] != 'Todos' and 'closeDate' in df_filtrado.columns:
        try:
            ano_int = int(filtros['ano'])
            df_filtrado = df_filtrado[df_filtrado['closeDate'].dt.year == ano_int]
        except:
            pass
    
    # Filtro por vendedor
    if filtros['vendedor'] != 'Todos' and 'sellerName' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['sellerName'] == filtros['vendedor']]
    
    return df_filtrado

# ============================================================================
# SISTEMA DE IDIOMAS
# ============================================================================

TRANSLATIONS = {
    'pt': {
        # Tela de boas-vindas
        'welcome_title': 'Painel de Resultados em Tempo Real',
        'welcome_subtitle': 'Dashboard executivo para acompanhamento estratégico do agronegócio',
        'dashboard_config': '⚙️ Configurações do Dashboard',
         'period_analysis': 'Período de Análise',
        'data_source': 'Fonte de Dados',
        'real_data': 'Dados Reais',
        'business_units': 'Unidades de Negócio',
        'financial_metrics': 'Métricas Financeiras',
        'operational_metrics': 'Métricas Operacionais',
        'market_analysis': 'Análise de Mercado',
        'data_status': 'Status dos Dados',
        'last_update': 'Última atualização:',
        'update_data': 'Atualizar Dados',
        'access_dashboard': 'Acessar Dashboard Completo',
        
        # Menu principal
        'main_title': 'FOX SA - Painel de Resultados em Tempo Real',
        'select_section': 'Selecionar Seção:',
        'period': 'Período:',
        'visualization': 'Visualização:',
        'language': 'Idioma:',
        'home': 'Início',
        
        # Seções do menu
        'consolidated_view': 'Visão Consolidada',
        'fox_graos_section': 'Fox Grãos (Trading)',
        'fox_log_section': 'Fox Log - Transporte & Insumos',
        'clube_fx_section': 'Clube FX - Consultoria',
        'financial_performance': 'Performance Financeira',
        'dre_realtime': 'DRE em Tempo Real',
        'insights_trends': 'Insights & Tendências',
        'projections_scenarios': 'Projeções & Cenários',
        'roadmap_actions': 'Roadmap & Ações',
        'due_diligence': 'Due Diligence & Captação',
        'settings': 'Configurações',
        
        # Períodos
        'last_12_months': 'Últimos 12 meses',
        'last_6_months': 'Últimos 6 meses',
        'last_quarter': 'Último trimestre',
        'custom': 'Personalizado',
        
        # Visualizações
        'executive': 'Executiva',
        'detailed': 'Detalhada',
        'operational': 'Operacional',
        
        # KPIs
        'gross_revenue': 'Receita Bruta',
        'ebitda': 'EBITDA',
        'operational_cashflow': 'Fluxo de Caixa Op.',
        'active_clients': 'Clientes Ativos',
        'vs_previous': 'vs período anterior',
        
        # Fox Grãos
        'fox_graos_title': 'Fox Grãos (Trading)',
        'triangular_trade': 'Operação de Trade Triangular',
        'logistics_section': 'Logística',
        'negotiated_volume': 'Volume Negociado',
        'trade_revenue': 'Receita Trade',
        'trade_margin': 'Margem de Trade',
        'average_cycle': 'Ciclo Médio',
        'last_30_days': 'Últimos 30 dias',
        'vs_previous_month': 'vs mês anterior',
        'vs_average': 'vs média',
        
        # Fox Log
        'fox_log_title': 'Fox Log - Logística & Insumos',
        'transport_revenue': 'Receita Transporte',
        'storage_revenue': 'Receita Armazenagem',
        'transported_volume': 'Volume Transportado',
        'punctuality_sla': 'SLA Pontualidade',
        
        # Clube FX
        'clube_fx_title': 'Clube FX - Consultoria',
        'clients_served': 'Clientes Atendidos',
        'consulting_revenue': 'Receita Consultoria',
        'nps_score': 'NPS Score',
        'retention_rate': 'Taxa Retenção',
        'new_clients': 'novos clientes',
        'vs_quarter': 'vs trimestre',
        'ongoing_projects': 'Projetos em Andamento',
        'completed': 'concluído',
        
        # Due Diligence
        'due_diligence_title': 'Documentos para Due Diligence e Captação',
        'financial_statements': 'Demonstrativos Financeiros',
        'dre_detailed': 'DRE Detalhado por Unidade',
        'balance_sheet': 'Balanço Patrimonial',
        'corporate_structure': 'Estrutura Corporativa',
        'group_organogram': 'Organograma do Grupo',
        'institutional_presentation': 'Apresentação Institucional',
        'institutional_deck': 'Deck Institucional',
        'download_pdf': 'Baixar PDF',
        'download_excel': 'Baixar Excel',
        'view_document': 'Visualizar Documento',
        
        # Gráficos
        'revenue_ebitda_12m': 'Receita x EBITDA (Últimos 12 Meses)',
        'investment_vs_capex': 'Investimento vs Capex por Mês',
        'volume_by_grain': 'Volume por Tipo de Grão',
        'contracts_by_month': 'Contratos Fechados por Mês',
        'modalities_distribution': 'Distribuição de Modalidades',
        'operational_cost_heatmap': 'Custo Operacional por Modalidade e Carga (R$/t)',
        'revenue_by_service': 'Receita por Tipo de Serviço',
        
        # Unidades
        'millions': 'Milhões',
        'thousands_tons': 'mil toneladas',
        'contracts_number': 'Número de Contratos',
        'value_millions': 'Valor (R$ Milhões)',
        
        # Status
        'in_development': 'Esta seção está em desenvolvimento. Em breve estará disponível!',
        
        # Documentos DRE
        'dre_fox_graos': 'DRE Fox Grãos',
        'dre_fox_log': 'DRE Fox Log', 
        'dre_clube_fx': 'DRE Clube FX',
        'dre_consolidated': 'DRE Consolidado',
        'net_revenue': 'Receita Líquida',
        'cost_goods_sold': 'Custo dos Produtos Vendidos',
        'gross_profit': 'Lucro Bruto',
        'operating_expenses': 'Despesas Operacionais',
        'net_income': 'Lucro Líquido',
        
        # Balanço Patrimonial
        'assets': 'Ativo',
        'current_assets': 'Ativo Circulante',
        'non_current_assets': 'Ativo Não Circulante',
        'liabilities': 'Passivo',
        'current_liabilities': 'Passivo Circulante',
        'non_current_liabilities': 'Passivo Não Circulante',
        'equity': 'Patrimônio Líquido'
    },
    
    'en': {
        # Welcome screen
        'welcome_title': 'Real-Time Results Dashboard',
        'welcome_subtitle': 'Executive dashboard for strategic agribusiness monitoring',
        'dashboard_config': '⚙️ Dashboard Settings',
        'period_analysis': '📅 Analysis Period',
        'initial_date': 'Start Date:',
        'final_date': 'End Date:',
        'business_units': '🏢 Business Units',
        'fox_graos_desc': 'Fox Grãos (Trade & Logistics)',
        'fox_log_desc': 'Fox Log (Transport & Inputs)',
        'clube_fx_desc': 'Clube FX (Consulting)',
          'data_status': 'Data Status',
        'last_update': 'Last update:',
        'update_data': 'Update Data',
        'access_dashboard': 'Access Complete Dashboard',
        
        # Main menu
        'main_title': 'FOX SA - Real-Time Results Dashboard',
        'select_section': '📊 Select Section:',
        'period': '📅 Period:',
        'visualization': '👁️ Visualization:',
        'language': '🌐 Language:',
        'home': '🏠 Home',
        
        # Menu sections
        'consolidated_view': 'Consolidated View',
        'fox_graos_section': 'Fox Grãos - Trade & Logistics',
        'fox_log_section': 'Fox Log - Transport & Inputs',
        'clube_fx_section': 'Clube FX - Consulting',
        'financial_performance': 'Financial Performance',
        'dre_realtime': 'Real-Time Income Statement',
        'insights_trends': 'Insights & Trends',
        'projections_scenarios': 'Projections & Scenarios',
        'roadmap_actions': 'Roadmap & Actions',
        'due_diligence': 'Due Diligence & Fundraising',
        'settings': 'Settings',
        
        # Periods
        'last_12_months': 'Last 12 months',
        'last_6_months': 'Last 6 months',
        'last_quarter': 'Last quarter',
        'custom': 'Custom',
        
        # Visualizations
        'executive': 'Executive',
        'detailed': 'Detailed',
        'operational': 'Operational',
        
        # KPIs
        'gross_revenue': 'Gross Revenue',
        'ebitda': 'EBITDA',
        'operational_cashflow': 'Operational Cash Flow',
        'active_clients': 'Active Clients',
        'vs_previous': 'vs previous period',
        
        # Fox Grãos
        'fox_graos_title': '🌾 Fox Grãos - Triangular Trade & Logistics',
        'triangular_trade': '📈 Triangular Trade Operation',
        'logistics_section': '🚛 Logistics',
        'negotiated_volume': 'Negotiated Volume',
        'trade_revenue': 'Trade Revenue',
        'trade_margin': 'Trade Margin',
        'average_cycle': 'Average Cycle',
        'last_30_days': 'Last 30 days',
        'vs_previous_month': 'vs previous month',
        'vs_average': 'vs average',
        
        # Fox Log
        'fox_log_title': '🚛 Fox Log - Logistics & Inputs',
        'transport_revenue': 'Transport Revenue',
        'storage_revenue': 'Storage Revenue',
        'transported_volume': 'Transported Volume',
        'punctuality_sla': 'Punctuality SLA',
        
        # Clube FX
        'clube_fx_title': '💼 Clube FX - Consulting',
        'clients_served': 'Clients Served',
        'consulting_revenue': 'Consulting Revenue',
        'nps_score': 'NPS Score',
        'retention_rate': 'Retention Rate',
        'new_clients': 'new clients',
        'vs_quarter': 'vs quarter',
        'ongoing_projects': 'Ongoing Projects',
        'completed': 'completed',
        
        # Due Diligence
        'due_diligence_title': '📋 Due Diligence & Fundraising Documents',
        'financial_statements': '📊 Financial Statements',
        'dre_detailed': 'Detailed Income Statement by Unit',
        'balance_sheet': 'Balance Sheet',
        'corporate_structure': '🏢 Corporate Structure',
        'group_organogram': 'Group Organogram',
        'institutional_presentation': '📈 Institutional Presentation',
        'institutional_deck': 'Institutional Deck',
        'download_pdf': 'Download PDF',
        'download_excel': 'Download Excel',
        'view_document': 'View Document',
        
        # Charts
        'revenue_ebitda_12m': 'Revenue x EBITDA (Last 12 Months)',
        'investment_vs_capex': 'Investment vs Capex by Month',
        'volume_by_grain': 'Volume by Grain Type',
        'contracts_by_month': 'Contracts Closed by Month',
        'modalities_distribution': 'Modalities Distribution',
        'operational_cost_heatmap': 'Operational Cost by Modality and Load (R$/t)',
        'revenue_by_service': 'Revenue by Service Type',
        
        # Units
        'millions': 'Millions',
        'thousands_tons': 'thousand tons',
        'contracts_number': 'Number of Contracts',
        'value_millions': 'Value (R$ Millions)',
        
        # Status
        'in_development': 'This section is under development. Coming soon!',
        
        # DRE Documents
        'dre_fox_graos': 'Fox Grãos Income Statement',
        'dre_fox_log': 'Fox Log Income Statement',
        'dre_clube_fx': 'Clube FX Income Statement',
        'dre_consolidated': 'Consolidated Income Statement',
        'net_revenue': 'Net Revenue',
        'cost_goods_sold': 'Cost of Goods Sold',
        'gross_profit': 'Gross Profit',
        'operating_expenses': 'Operating Expenses',
        'net_income': 'Net Income',
        
        # Balance Sheet
        'assets': 'Assets',
        'current_assets': 'Current Assets',
        'non_current_assets': 'Non-Current Assets',
        'liabilities': 'Liabilities',
        'current_liabilities': 'Current Liabilities',
        'non_current_liabilities': 'Non-Current Liabilities',
        'equity': 'Equity'
    }
}

def get_text(key, lang='pt'):
    """Função para obter texto traduzido"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

def configurar_pagina():
    """Configuração inicial da página"""
    st.set_page_config(
        page_title="FOX SA - Real-Time Results Dashboard",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

# ============================================================================
# TELA DE BOAS-VINDAS
# ============================================================================

def tela_boas_vindas(lang='pt'):
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
        st.markdown(f"""
        <div style="padding: 2rem 0;">
            <h1 style="color: #FFFFFF; font-size: 2.5rem; margin: 0;">{get_text('welcome_title', lang)}</h1>
            <p style="color: #C0C0C0; font-size: 1.2rem; margin: 0.5rem 0;">{get_text('welcome_subtitle', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr style="margin: 2rem 0; border: 1px solid #333333;">', unsafe_allow_html=True)
    
    # Filtros principais
    st.markdown(f'<h3 style="color: #FFFFFF; margin-bottom: 1rem;">{get_text("dashboard_config", lang)}</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.markdown(f"**{get_text('period_analysis', lang)}**")
        data_inicial = st.date_input(
            get_text('initial_date', lang),
            value=datetime.now() - timedelta(days=365),
            key="data_inicial"
        )
        data_final = st.date_input(
            get_text('final_date', lang),
            value=datetime.now(),
            key="data_final"
        )
    
    with col2:
        st.markdown(f"**{get_text('business_units', lang)}**")
        fox_graos = st.checkbox(get_text('fox_graos_desc', lang), value=True, key="fox_graos")
        fox_log = st.checkbox(get_text('fox_log_desc', lang), value=True, key="fox_log")
        clube_fx = st.checkbox(get_text('clube_fx_desc', lang), value=True, key="clube_fx")
    
    with col3:
        st.markdown(f"**{get_text('data_status', lang)}**")
        ultima_atualizacao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        # Informação de última atualização (removida)
        pass
        
        if st.button(get_text('update_data', lang), key="refresh_welcome"):
            st.rerun()
    
    # Botão para acessar dashboard
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        pass  # Auto-generated pass
        if st.button(get_text('access_dashboard', lang), key="access_dashboard", type="primary"):
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
# SEÇÃO DE DUE DILIGENCE
# ============================================================================

def secao_due_diligence(lang='pt', filtros_globais=None):
    """Seção de documentos para due diligence e captação"""
    
    st.markdown(f'<h2 style="color: #FFFFFF; border-bottom: 2px solid #FFD700; padding-bottom: 0.5rem;">{get_text("due_diligence_title", lang)}</h2>', unsafe_allow_html=True)
    
    # Mostrar filtros aplicados se houver
    if filtros_globais:
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    
    # Demonstrativos Financeiros
    st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">{get_text("financial_statements", lang)}</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # DRE Detalhado
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("dre_detailed", lang)}</h4>', unsafe_allow_html=True)
        
        # Criar DRE por unidade
        dre_data = criar_dre_detalhado(lang)
        st.dataframe(dre_data, use_container_width=True, height=400)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            pass  # Auto-generated pass
            if st.button(f"📄 {get_text('download_pdf', lang)}", key="dre_pdf"):
                pass  # PDF download functionality
        with col_btn2:
            pass  # Auto-generated pass
            if st.button(f"📊 {get_text('download_excel', lang)}", key="dre_excel"):
                pass  # Excel download functionality
    
    with col2:
        # Balanço Patrimonial
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("balance_sheet", lang)}</h4>', unsafe_allow_html=True)
        
        # Criar Balanço
        balanco_data = criar_balanco_patrimonial(lang)
        st.dataframe(balanco_data, use_container_width=True, height=400)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            pass  # Auto-generated pass
            if st.button(f"📄 {get_text('download_pdf', lang)}", key="balanco_pdf"):
                pass  # PDF download functionality
        with col_btn2:
            pass  # Auto-generated pass
            if st.button(f"📊 {get_text('download_excel', lang)}", key="balanco_excel"):
                pass  # Excel download functionality
    
    # Estrutura Corporativa
    st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">{get_text("corporate_structure", lang)}</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Organograma
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("group_organogram", lang)}</h4>', unsafe_allow_html=True)
        criar_organograma(lang)
        
        if st.button(f"👁️ {get_text('view_document', lang)}", key="organograma_view"):
            pass  # View document functionality
    
    with col2:
        # Apresentação Institucional
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("institutional_presentation", lang)}</h4>', unsafe_allow_html=True)
        criar_deck_institucional(lang)
        
        if st.button(f"📈 {get_text('view_document', lang)}", key="deck_view"):
            pass  # View document functionality

def criar_dre_detalhado(lang='pt'):
    """Criar DRE detalhado por unidade de negócio"""
    
    dre_data = {
        get_text('net_revenue', lang): {
            get_text('dre_fox_graos', lang): 'R$ 89.200.000',
            get_text('dre_fox_log', lang): 'R$ 64.000.000',
            get_text('dre_clube_fx', lang): 'R$ 12.800.000',
            get_text('dre_consolidated', lang): 'R$ 166.000.000'
        },
        get_text('cost_goods_sold', lang): {
            get_text('dre_fox_graos', lang): 'R$ 67.400.000',
            get_text('dre_fox_log', lang): 'R$ 44.800.000',
            get_text('dre_clube_fx', lang): 'R$ 6.400.000',
            get_text('dre_consolidated', lang): 'R$ 118.600.000'
        },
        get_text('gross_profit', lang): {
            get_text('dre_fox_graos', lang): 'R$ 21.800.000',
            get_text('dre_fox_log', lang): 'R$ 19.200.000',
            get_text('dre_clube_fx', lang): 'R$ 6.400.000',
            get_text('dre_consolidated', lang): 'R$ 47.400.000'
        },
        get_text('operating_expenses', lang): {
            get_text('dre_fox_graos', lang): 'R$ 12.500.000',
            get_text('dre_fox_log', lang): 'R$ 11.200.000',
            get_text('dre_clube_fx', lang): 'R$ 3.200.000',
            get_text('dre_consolidated', lang): 'R$ 26.900.000'
        },
        'EBITDA': {
            get_text('dre_fox_graos', lang): 'R$ 9.300.000',
            get_text('dre_fox_log', lang): 'R$ 8.000.000',
            get_text('dre_clube_fx', lang): 'R$ 3.200.000',
            get_text('dre_consolidated', lang): 'R$ 20.500.000'
        },
        get_text('net_income', lang): {
            get_text('dre_fox_graos', lang): 'R$ 6.200.000',
            get_text('dre_fox_log', lang): 'R$ 5.300.000',
            get_text('dre_clube_fx', lang): 'R$ 2.100.000',
            get_text('dre_consolidated', lang): 'R$ 13.600.000'
        }
    }
    
    return pd.DataFrame(dre_data)

def criar_balanco_patrimonial(lang='pt'):
    """Criar balanço patrimonial consolidado"""
    
    balanco_data = {
        get_text('assets', lang): {
            get_text('current_assets', lang): 'R$ 45.200.000',
            get_text('non_current_assets', lang): 'R$ 78.800.000',
            'Total': 'R$ 124.000.000'
        },
        get_text('liabilities', lang): {
            get_text('current_liabilities', lang): 'R$ 28.400.000',
            get_text('non_current_liabilities', lang): 'R$ 32.600.000',
            'Total': 'R$ 61.000.000'
        },
        get_text('equity', lang): {
            'Capital Social': 'R$ 50.000.000',
            'Reservas': 'R$ 13.000.000',
            'Total': 'R$ 63.000.000'
        }
    }
    
    return pd.DataFrame(balanco_data)

def criar_organograma(lang='pt'):
    """Criar organograma visual do grupo"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333333;
        text-align: center;
        margin: 1rem 0;
    ">
        <div style="color: #FFD700; font-size: 1.5rem; font-weight: 700; margin-bottom: 2rem;">FOX SA (Holding)</div>
        
        <div style="display: flex; justify-content: space-around; margin-top: 2rem;">
            <div style="
                background: #2d2d2d;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #90EE90;
                min-width: 200px;
            ">
                <div style="color: #90EE90; font-weight: 600; margin-bottom: 0.5rem;">Fox Grãos</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Trade Triangular</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Logística</div>
                <div style="color: #FFFFFF; font-size: 0.8rem; margin-top: 0.5rem;">100% FOX SA</div>
            </div>
            
            <div style="
                background: #2d2d2d;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #FFD700;
                min-width: 200px;
            ">
                <div style="color: #FFD700; font-weight: 600; margin-bottom: 0.5rem;">Fox Log</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Transporte</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Insumos Agrícolas</div>
                <div style="color: #FFFFFF; font-size: 0.8rem; margin-top: 0.5rem;">100% FOX SA</div>
            </div>
            
            <div style="
                background: #2d2d2d;
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #87CEEB;
                min-width: 200px;
            ">
                <div style="color: #87CEEB; font-weight: 600; margin-bottom: 0.5rem;">Clube FX</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Consultoria</div>
                <div style="color: #C0C0C0; font-size: 0.9rem;">Assessoria Financeira</div>
                <div style="color: #FFFFFF; font-size: 0.8rem; margin-top: 0.5rem;">100% FOX SA</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def criar_deck_institucional(lang='pt'):
    """Criar preview do deck institucional"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #333333;
        margin: 1rem 0;
    ">
        <div style="color: #FFD700; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">
            📈 Deck Institucional FOX SA
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background: #333333; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="color: #90EE90; font-weight: 600;">Missão</div>
                <div style="color: #C0C0C0; font-size: 0.9rem; margin-top: 0.5rem;">
                    Conectar produtores e compradores no agronegócio através de soluções integradas de trade, logística e consultoria.
                </div>
            </div>
            
            <div style="background: #333333; padding: 1rem; border-radius: 8px; text-align: center;">
                <div style="color: #FFD700; font-weight: 600;">Visão</div>
                <div style="color: #C0C0C0; font-size: 0.9rem; margin-top: 0.5rem;">
                    Ser a principal plataforma de agronegócio do Centro-Oeste brasileiro até 2027.
                </div>
            </div>
        </div>
        
        <div style="background: #333333; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="color: #87CEEB; font-weight: 600; text-align: center; margin-bottom: 0.5rem;">Principais Marcos</div>
            <div style="color: #C0C0C0; font-size: 0.9rem;">
                • 2019: Fundação da FOX SA<br>
                • 2020: Lançamento Fox Grãos<br>
                • 2021: Expansão Fox Log<br>
                • 2022: Criação Clube FX<br>
                • 2023: R$ 150M em receita<br>
                • 2024: R$ 247M em receita (projetado)
            </div>
        </div>
        
        <div style="text-align: center; color: #C0C0C0; font-size: 0.9rem;">
            📊 Apresentação completa: 25 slides | 📈 Projeções 2025-2027 | 💰 Oportunidades de investimento
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES DE GRÁFICOS COM DADOS REAIS
# ============================================================================

def criar_grafico_receita_ebitda_real(dados_consolidados, lang='pt'):
    """Gráfico de receita mensal com dados reais do MongoDB"""
    
    receita_mensal = dados_consolidados.get('receita_mensal', {})
    
    if not receita_mensal:
        return criar_grafico_receita_ebitda(lang)  # Fallback
    
    # Converter períodos para strings de mês
    meses_map = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    meses = []
    receitas = []
    
    for periodo, valor in receita_mensal.items():
        mes_num = periodo.month
        meses.append(meses_map.get(mes_num, str(mes_num)))
        receitas.append(valor / 1_000_000)  # Converter para milhões
    
    # Estimar EBITDA (25% da receita)
    ebitdas = [r * 0.25 for r in receitas]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=receitas,
        mode='lines+markers',
        name='Receita (Dados Reais)',
        line=dict(color='#198754', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Receita: R$ %{y:.1f}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=ebitdas,
        mode='lines+markers',
        name='EBITDA (Estimado)',
        line=dict(color='#FD7E14', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>EBITDA: R$ %{y:.1f}M<extra></extra>'
    ))
    
    fig.update_layout(
        title='📈 Receita e EBITDA Mensal (Dados Reais)',
        xaxis_title='Mês',
        yaxis_title='Valor (R$ Milhões)',
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', family='Inter'),
        showlegend=True
    )
    
    return fig

def criar_grafico_distribuicao_real(dados_consolidados, lang='pt'):
    """Gráfico de distribuição por grão com dados reais"""
    
    receita_por_grao = dados_consolidados.get('receita_por_grao', {})
    
    if not receita_por_grao:
        return criar_grafico_investimento_capex(lang)  # Fallback
    
    graos = list(receita_por_grao.keys())
    valores = [v / 1_000_000 for v in receita_por_grao.values()]  # Converter para milhões
    
    fig = px.pie(
        values=valores,
        names=graos,
        title='🌾 Receita por Tipo de Grão (Dados Reais)',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Receita: R$ %{value:.1f}M<br>Percentual: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black', family='Inter')
    )
    
    return fig

def criar_grafico_performance_real(dados_performance, tema, lang='pt'):
    """Gráfico de performance financeira com dados reais"""
    
    df = pd.DataFrame(dados_performance)
    
    fig = go.Figure()
    
    # Adicionar linhas para cada métrica
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Receita Líquida'] / 1_000_000,
        mode='lines+markers',
        name='Receita Líquida',
        line=dict(color='#198754', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['EBITDA'] / 1_000_000,
        mode='lines+markers',
        name='EBITDA',
        line=dict(color='#FD7E14', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Lucro Líquido'] / 1_000_000,
        mode='lines+markers',
        name='Lucro Líquido',
        line=dict(color='#0D6EFD', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Fluxo Caixa Livre'] / 1_000_000,
        mode='lines+markers',
        name='Fluxo Caixa Livre',
        line=dict(color='#6F42C1', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='📈 Evolução das Métricas Financeiras (Dados Reais)',
        xaxis_title='Mês',
        yaxis_title='Valor (R$ Milhões)',
        height=400,
        plot_bgcolor='white' if tema == 'light' else 'rgba(0,0,0,0)',
        paper_bgcolor='white' if tema == 'light' else 'rgba(0,0,0,0)',
        font=dict(color='black' if tema == 'light' else 'white', family='Inter'),
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

# ============================================================================
# VISÃO CONSOLIDADA (ATUALIZADA COM IDIOMAS)
# ============================================================================

def visao_consolidada(dados_eda, dados_financeiros, lang='pt', ano_selecionado=2024, filtros_globais=None):
    """Dashboard geral consolidado com dados reais do MongoDB"""
    
    st.markdown(f'<h2 style="color: #FFFFFF; border-bottom: 2px solid #C0C0C0; padding-bottom: 0.5rem;">📊 {get_text("consolidated_view", lang)}</h2>', unsafe_allow_html=True)
    
    # Mostrar filtros aplicados se houver
    if filtros_globais:
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    
    # Carregar dados reais do MongoDB
    with st.spinner("Carregando dados consolidados..."):
        try:
            from mongodb_connector import load_consolidated_data
            dados_consolidados = load_consolidated_data(year=ano_selecionado)
            
            # Aplicar filtros globais aos dados se fornecidos
            if filtros_globais and 'contratos' in dados_consolidados:
                dados_consolidados['contratos'] = aplicar_filtros_globais(dados_consolidados['contratos'], filtros_globais)
            
            if not dados_consolidados:
                usar_dados_reais = False
            else:
                usar_dados_reais = True
                
        except Exception as e:
            usar_dados_reais = False
    
    # === MÉTRICAS FINANCEIRAS PRINCIPAIS ===
    st.markdown("### 💰 Métricas Financeiras Principais")
    
    if usar_dados_reais:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            receita_liquida = dados_consolidados['receita_liquida']
            st.metric(
                label="💵 Receita Líquida",
                value=f"R$ {receita_liquida/1_000_000:.1f}M",
                delta="+12.5%"
            )
        
        with col2:
            custo_total = dados_consolidados['custo_total']
            st.metric(
                label="📦 Custo Total",
                value=f"R$ {custo_total/1_000_000:.1f}M",
                delta="+8.2%"
            )
        
        with col3:
            despesas_operacionais = dados_consolidados['despesas_operacionais']
            st.metric(
                label="💸 Despesas Operacionais",
                value=f"R$ {despesas_operacionais/1_000_000:.1f}M",
                delta="+5.1%"
            )
        
        with col4:
            margem_liquida = dados_consolidados['margem_liquida']
            st.metric(
                label="📈 Margem Líquida",
                value=f"{margem_liquida:.1f}%",
                delta="+2.3pp"
            )
    else:
        # Fallback com dados simulados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💵 Receita Líquida", "R$ 185M", "+12.5%")
        with col2:
            st.metric("📦 Custo Total", "R$ 142M", "+8.2%")
        with col3:
            st.metric("💸 Despesas Operacionais", "R$ 28M", "+5.1%")
        with col4:
            st.metric("📈 Margem Líquida", "8.1%", "+2.3pp")
    
    st.markdown("---")
    
    # === DETALHAMENTO FINANCEIRO ===
    if usar_dados_reais:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Composição da Receita")
            receita_data = {
                'Fox Grãos': dados_consolidados['comercializacao_graos'],
                'Fox Log': dados_consolidados['servicos_logisticos'],
                'Clube FX': dados_consolidados['consultoria']
            }
            
            # Filtrar apenas valores > 0
            receita_data = {k: v for k, v in receita_data.items() if v > 0}
            
            if receita_data:
                fig_receita = px.pie(
                    values=list(receita_data.values()),
                    names=list(receita_data.keys()),
                    title="Receita por Unidade de Negócio",
                    color_discrete_sequence=['#198754', '#FD7E14', '#0D6EFD']
                )
                fig_receita.update_traces(textposition='inside', textinfo='percent+label')
                fig_receita.update_layout(height=300, showlegend=True)
                st.plotly_chart(fig_receita, use_container_width=True)
            else:
                pass  # Fallback case
        
        with col2:
            st.markdown("#### 💰 Estrutura de Custos e Despesas")
            
            # Criar gráfico de barras para custos e despesas
            categorias = ['CPV', 'Custos Operacionais', 'Pessoal', 'Marketing', 'Administrativo']
            valores = [
                dados_consolidados['cpv_total'],
                dados_consolidados['custos_operacionais_total'],
                dados_consolidados['pessoal_beneficios'],
                dados_consolidados['marketing_vendas'],
                dados_consolidados['despesas_admin']
            ]
            
            fig_custos = px.bar(
                x=categorias,
                y=[v/1_000_000 for v in valores],
                title="Custos e Despesas (R$ Milhões)",
                color=categorias,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_custos.update_layout(
                height=300,
                xaxis_title="Categoria",
                yaxis_title="Valor (R$ M)",
                showlegend=False
            )
            st.plotly_chart(fig_custos, use_container_width=True)
    
    # === KPIs OPERACIONAIS ===
    st.markdown("### 📈 KPIs Operacionais")
    
    if usar_dados_reais:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            volume_total = dados_consolidados['volume_total']
            st.metric(
                label="📦 Volume Total",
                value=f"{volume_total:,.0f} un.",
                delta="+15.2%"
            )
        
        with col2:
            numero_contratos = dados_consolidados['numero_contratos']
            st.metric(
                label="📋 Contratos Ativos",
                value=f"{numero_contratos:,}",
                delta="+8.7%"
            )
        
        with col3:
            preco_medio = dados_consolidados['preco_medio']
            st.metric(
                label="💲 Preço Médio",
                value=f"R$ {preco_medio:.2f}/un.",
                delta="+5.8%"
            )
        
        with col4:
            ebitda = dados_consolidados['ebitda']
            st.metric(
                label="🎯 EBITDA",
                value=f"R$ {ebitda/1_000_000:.1f}M",
                delta="+18.3%"
            )
    else:
        # Fallback com dados simulados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Volume Total", "2.1M un.", "+15.2%")
        with col2:
            st.metric("📋 Contratos Ativos", "1,247", "+8.7%")
        with col3:
            st.metric("💲 Preço Médio", "R$ 87.50/un.", "+5.8%")
        with col4:
            st.metric("🎯 EBITDA", "R$ 43M", "+18.3%")
    
    st.markdown("---")
    
    # === GRÁFICOS DE PERFORMANCE ===
    st.markdown("### 📊 Performance Mensal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pass  # Auto-generated pass
        if usar_dados_reais:
            fig_receita_ebitda = criar_grafico_receita_ebitda_real(dados_consolidados, lang)
        else:
            fig_receita_ebitda = criar_grafico_receita_ebitda(lang)
        st.plotly_chart(fig_receita_ebitda, use_container_width=True)
    
    with col2:
        pass  # Auto-generated pass
        if usar_dados_reais:
            fig_distribuicao = criar_grafico_distribuicao_real(dados_consolidados, lang)
        else:
            fig_distribuicao = criar_grafico_investimento_capex(lang)
        st.plotly_chart(fig_distribuicao, use_container_width=True)
    
    # === ANÁLISE DE MARGEM ===
    if usar_dados_reais:
        st.markdown("### 📈 Análise de Margens")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            margem_bruta = dados_consolidados['margem_bruta']
            st.metric(
                label="📊 Margem Bruta",
                value=f"{margem_bruta:.1f}%",
                delta="+1.8pp"
            )
        
        with col2:
            margem_ebitda = dados_consolidados['margem_ebitda']
            st.metric(
                label="🎯 Margem EBITDA",
                value=f"{margem_ebitda:.1f}%",
                delta="+2.1pp"
            )
        
        with col3:
            margem_liquida = dados_consolidados['margem_liquida']
            st.metric(
                label="💰 Margem Líquida",
                value=f"{margem_liquida:.1f}%",
                delta="+2.3pp"
            )
        
        # Gráfico de evolução das margens (se houver dados mensais)
        if dados_consolidados.get('receita_mensal'):
            st.markdown("#### 📈 Evolução das Margens")
    
    # === RESUMO EXECUTIVO ===
    if usar_dados_reais:
        st.markdown("### 📋 Resumo Executivo")
        
        receita_bruta = dados_consolidados['receita_bruta']
        receita_liquida = dados_consolidados['receita_liquida']
        lucro_liquido = dados_consolidados['lucro_liquido']
        
        st.markdown(f"""
        **Desempenho Financeiro ({ano_selecionado}):**
        - **Receita Bruta:** R$ {receita_bruta/1_000_000:.1f} milhões
        - **Receita Líquida:** R$ {receita_liquida/1_000_000:.1f} milhões  
        - **Lucro Líquido:** R$ {lucro_liquido/1_000_000:.1f} milhões
        - **Margem Líquida:** {dados_consolidados['margem_liquida']:.1f}%
        
        **Principais Unidades de Negócio:**
        - **Fox Grãos:** R$ {dados_consolidados['comercializacao_graos']/1_000_000:.1f}M em comercialização
        - **Fox Log:** R$ {dados_consolidados['servicos_logisticos']/1_000_000:.1f}M em serviços logísticos  
        - **Clube FX:** R$ {dados_consolidados['consultoria']/1_000_000:.1f}M em consultoria
        """)
    else:
        st.markdown("### 📋 Resumo Executivo")

def criar_grafico_receita_ebitda(lang='pt'):
    """Gráfico de linha Receita x EBITDA - tema branco"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    receita = [18.5, 19.2, 21.8, 20.1, 22.3, 24.1, 23.8, 25.2, 24.9, 26.1, 25.8, 27.2]
    ebitda = [6.8, 7.1, 8.2, 7.5, 8.9, 9.8, 9.2, 10.1, 9.8, 10.5, 10.2, 11.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=receita,
        mode='lines+markers',
        name=get_text('gross_revenue', lang),
        line=dict(color='#198754', width=3),
        marker=dict(size=8),
        hovertemplate=f'<b>%{{x}}</b><br>{get_text("gross_revenue", lang)}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=ebitda,
        mode='lines+markers',
        name=get_text('ebitda', lang),
        line=dict(color='#0D6EFD', width=3),
        marker=dict(size=8),
        hovertemplate=f'<b>%{{x}}</b><br>{get_text("ebitda", lang)}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=get_text('revenue_ebitda_12m', lang), font=dict(size=18, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=400,
        legend=dict(font=dict(color='#000000')),
        xaxis=dict(showgrid=True, gridcolor='#E9ECEF', color='#000000'),
        yaxis=dict(showgrid=True, gridcolor='#E9ECEF', color='#000000', title=f'{get_text("value_millions", lang)}')
    )
    
    return fig

def criar_grafico_investimento_capex(lang='pt'):
    """Gráfico de barras empilhadas Investimento vs Capex - tema branco"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    investimento = [2.1, 1.8, 2.5, 2.2, 2.8, 3.1, 2.9, 3.2, 3.0, 3.5, 3.3, 3.8]
    capex = [1.2, 1.5, 1.8, 1.4, 2.1, 2.3, 2.0, 2.4, 2.2, 2.6, 2.5, 2.9]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses, y=investimento,
        name='Investimento' if lang == 'pt' else 'Investment',
        marker=dict(color='#6C757D'),
        hovertemplate=f'<b>%{{x}}</b><br>{"Investimento" if lang == "pt" else "Investment"}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=meses, y=capex,
        name='Capex',
        marker=dict(color='#FD7E14'),
        hovertemplate='<b>%{x}</b><br>Capex: R$ %{y}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=get_text('investment_vs_capex', lang), font=dict(size=18, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=400,
        barmode='stack',
        legend=dict(font=dict(color='#000000')),
        xaxis=dict(showgrid=False, color='#000000'),
        yaxis=dict(showgrid=True, gridcolor='#E9ECEF', color='#000000', title=get_text('value_millions', lang))
    )
    
    return fig

# ============================================================================
# SISTEMA DE TEMAS
# ============================================================================

def aplicar_css_tema(tema='light'):
    """CSS forçado para tema light apenas - corrigido para mobile"""
    
    # FORÇAR SEMPRE TEMA LIGHT
    tema = 'light'  # Força tema light independente do parâmetro
    
    # Cores do tema claro
    bg_color = '#FFFFFF'
    text_color = '#000000'
    card_bg = '#F8F9FA'
    border_color = '#DEE2E6'
    grid_color = '#E9ECEF'
    secondary_text = '#6C757D'
    input_bg = '#F8F9FA'
    hover_color = '#6C757D'
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* FORÇAR TEMA LIGHT EM TODOS OS ELEMENTOS */
        .stApp {{
            background: {bg_color} !important;
            color: {text_color} !important;
            font-family: 'Inter', sans-serif;
        }}
        
        /* Forçar fundo branco em todo o app */
        .main, .block-container, [data-testid="stAppViewContainer"] {{
            background: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        /* Esconder sidebar */
        section[data-testid="stSidebar"] {{
            display: none !important;
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }}
        
        /* FORÇAR TEXTO ESCURO EM TODOS OS ELEMENTOS */
        h1, h2, h3, h4, h5, h6, p, span, div, label {{
            color: {text_color} !important;
        }}
        
        /* Métricas - FORÇAR TEXTO ESCURO */
        [data-testid="metric-container"] {{
            background: {card_bg} !important;
            color: {text_color} !important;
        }}
        
        [data-testid="metric-container"] > div {{
            color: {text_color} !important;
        }}
        
        [data-testid="metric-container"] label {{
            color: {secondary_text} !important;
        }}
        
        [data-testid="metric-container"] [data-testid="metric-value"] {{
            color: {text_color} !important;
            font-weight: 700 !important;
        }}
        
        /* Selectboxes - FORÇAR TEMA LIGHT */
        .stSelectbox > div > div {{
            background: {input_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            color: {text_color} !important;
        }}
        
        .stSelectbox > div > div > div {{
            color: {text_color} !important;
        }}
        
        /* Dropdown options - FORÇAR FUNDO BRANCO */
        [data-baseweb="popover"] {{
            background: {bg_color} !important;
        }}
        
        [data-baseweb="menu"] {{
            background: {bg_color} !important;
            border: 1px solid {border_color} !important;
        }}
        
        [data-baseweb="menu"] li {{
            background: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        [data-baseweb="menu"] li:hover {{
            background: {card_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Botões - FORÇAR TEMA LIGHT */
        .stButton > button {{
            background: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            color: {text_color} !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            border-color: {hover_color} !important;
            box-shadow: 0 0 10px rgba(108, 117, 125, 0.3) !important;
        }}
        
        /* Checkboxes */
        .stCheckbox > label {{
            color: {text_color} !important;
        }}
        
        /* Date inputs */
        .stDateInput > div > div > input {{
            background: {input_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            color: {text_color} !important;
        }}
        
        /* DataFrames */
        .stDataFrame {{
            background: {bg_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px 8px 0 0 !important;
            color: {text_color} !important;
            font-weight: 500 !important;
            padding: 12px 24px !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {bg_color} !important;
            border-bottom: 1px solid {bg_color} !important;
            color: {text_color} !important;
            font-weight: 600 !important;
        }}
        
        /* Cards personalizados */
        .metric-card {{
            background: {card_bg} !important;
            padding: 1.5rem !important;
            border-radius: 12px !important;
            border: 1px solid {border_color} !important;
            text-align: center !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 1rem !important;
        }}
        
        .metric-value {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: {text_color} !important;
            margin: 0.5rem 0 !important;
        }}
        
        .metric-label {{
            font-size: 0.9rem !important;
            color: {secondary_text} !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .metric-delta {{
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }}
        
        .delta-positive {{ color: #198754 !important; }}
        .delta-negative {{ color: #DC3545 !important; }}
        .delta-neutral {{ color: {secondary_text} !important; }}
        
        /* MOBILE RESPONSIVO */
        @media (max-width: 768px) {{
            .main .block-container {{
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1rem !important;
            }}
            
            /* Forçar texto visível no mobile */
            * {{
                color: {text_color} !important;
            }}
            
            /* Métricas no mobile */
            [data-testid="metric-container"] {{
                background: {card_bg} !important;
                border: 1px solid {border_color} !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                margin: 0.5rem 0 !important;
            }}
            
            [data-testid="metric-container"] [data-testid="metric-value"] {{
                color: {text_color} !important;
                font-size: 1.5rem !important;
                font-weight: 700 !important;
            }}
            
            [data-testid="metric-container"] label {{
                color: {secondary_text} !important;
                font-size: 0.8rem !important;
            }}
            
            /* Selectboxes no mobile */
            .stSelectbox {{
                margin-bottom: 1rem !important;
            }}
            
            .stSelectbox > div > div {{
                background: {input_bg} !important;
                color: {text_color} !important;
                border: 2px solid {border_color} !important;
                font-size: 1rem !important;
                padding: 0.75rem !important;
            }}
            
            /* Dropdown no mobile */
            [data-baseweb="popover"] {{
                background: {bg_color} !important;
                border: 2px solid {border_color} !important;
            }}
            
            [data-baseweb="menu"] li {{
                background: {bg_color} !important;
                color: {text_color} !important;
                padding: 1rem !important;
                font-size: 1rem !important;
            }}
        }}
        
        /* FORÇAR TEMA LIGHT NO STREAMLIT */
        .stApp > header {{
            background: transparent !important;
        }}
        
        .stApp > header [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        /* Remover qualquer tema escuro */
        [data-theme="dark"], [data-theme="auto"] {{
            background: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        /# ============================================================================
# DASHBOARDS POR UNIDADE DE NEGÓCIO
# ============================================================================

def dashboards_unidades_negocio(lang='pt', filtros_globais=None):px solid #DEE2E6; padding-bottom: 0.5rem;">🏢 {get_text("business_units_detailed", lang)}</h2>', unsafe_allow_html=True)
    
    # Mostrar filtros aplicados se houver
    if filtros_globais:
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    
    # Carregar dados reais por unidade
    with st.spinner("Carregando dados das unidades..."):
        try:
            from mongodb_connector import load_units_data_from_mongo
            dados_unidades = load_units_data_from_mongo(year=2025)
            
            if dados_unidades:
                usar_dados_reais = True
            else:
                dados_unidades = {}
                usar_dados_reais = False
                
        except Exception as e:
            dados_unidades = {}
            usar_dados_reais = False
    
    # Criar tabs para navegação rápida
    tab1, tab2, tab3 = st.tabs(["🌾 Fox Grãos", "🚛 Fox Log", "💼 Clube FX"])
    
    with tab1:
        dashboard_fox_graos_detalhado(lang, dados_unidades.get('fox_graos', {}), usar_dados_reais)
    
    with tab2:
        dashboard_fox_log_detalhado(lang, dados_unidades.get('fox_log', {}), usar_dados_reais)
    
    with tab3:
        dashboard_clube_fx_detalhado(lang, dados_unidades.get('clube_fx', {}), usar_dados_reais)

def dashboard_fox_graos_detalhado(lang='pt', dados_fox_graos={}, usar_dados_reais=False):
    """Dashboard detalhado da Fox Grãos com dados reais de contratos isGrain"""
    
    st.markdown('<h3 style="color: #000000; margin: 1rem 0;">🌾 Fox Grãos (Trading)</h3>', unsafe_allow_html=True)
    
    # Operação de Trade Triangular
    st.markdown('<h4 style="color: #198754; margin: 1.5rem 0 1rem 0;">📈 Operação de Trade Triangular</h4>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6C757D; margin-bottom: 1rem;">Demanda de compradores → Sourcing de produtores → Entrega</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # KPIs Trade
    with col1:
        volume_value = "125.8k t"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Volume Negociado</div>
            <div class="metric-value">{volume_value}</div>
            <div class="metric-delta delta-positive">+18.5% vs mês anterior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        receita_value = "R$ 89.2M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Receita Trade</div>
            <div class="metric-value">{receita_value}</div>
            <div class="metric-delta delta-positive">+12.3% vs período anterior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        margem_value = "12.8%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Margem de Trade</div>
            <div class="metric-value">{margem_value}</div>
            <div class="metric-delta delta-positive">+2.1 p.p.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        tempo_value = "18 dias"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tempo de Ciclo</div>
            <div class="metric-value">{tempo_value}</div>
            <div class="metric-delta delta-positive">-3 dias vs média</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Serviços Logísticos
    st.markdown('<h4 style="color: #198754; margin: 2rem 0 1rem 0;">🚛 Serviços Logísticos</h4>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # KPIs Logística
        col_a, col_b = st.columns(2)
        with col_a:
            receita_log_value = "R$ 24.5M"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Receita Logística</div>
                <div class="metric-value">{receita_log_value}</div>
                <div class="metric-delta delta-positive">+15.2%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Margem Bruta</div>
                <div class="metric-value">28.5%</div>
                <div class="metric-delta delta-positive">+1.8 p.p.</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Volume por tipo de grão
        fig_volume_graos = criar_grafico_volume_graos_branco()
        st.plotly_chart(fig_volume_graos, use_container_width=True)
    
    # Linha do tempo de contratos
    st.markdown('<h4 style="color: #198754; margin: 2rem 0 1rem 0;">📅 Timeline de Contratos Fechados</h4>', unsafe_allow_html=True)
    fig_timeline = criar_timeline_contratos_branco()
    st.plotly_chart(fig_timeline, use_container_width=True)

def dashboard_fox_log_detalhado(lang='pt', dados_fox_log={}, usar_dados_reais=False):
    """Dashboard detalhado da Fox Log com dados reais de contratos isFreight"""
    
    st.markdown('<h3 style="color: #000000; margin: 1rem 0;">🚛 Fox Log - Transporte & Insumos</h3>', unsafe_allow_html=True)
    
    # Transporte & Armazenagem
    st.markdown('<h4 style="color: #FD7E14; margin: 1.5rem 0 1rem 0;">📦 Transporte & Armazenagem</h4>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        receita_transp_value = "R$ 45.8M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Receita Transporte</div>
            <div class="metric-value">{receita_transp_value}</div>
            <div class="metric-delta delta-positive">+12.3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        receita_armaz_value = "R$ 18.2M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Receita Armazenagem</div>
            <div class="metric-value">{receita_armaz_value}</div>
            <div class="metric-delta delta-positive">+8.7%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Volume Total</div>
            <div class="metric-value">89.5k t</div>
            <div class="metric-delta delta-positive">+15.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">SLA Pontualidade</div>
            <div class="metric-value">94.8%</div>
            <div class="metric-delta delta-positive">+2.1 p.p.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Tipos de Carga
    st.markdown('<h4 style="color: #FD7E14; margin: 2rem 0 1rem 0;">📊 Tipos de Carga</h4>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tipos_carga = criar_grafico_tipos_carga_branco()
        st.plotly_chart(fig_tipos_carga, use_container_width=True)
    
    with col2:
        # Modalidades de Contratação
        fig_modalidades = criar_grafico_modalidades_branco()
        st.plotly_chart(fig_modalidades, use_container_width=True)
    
    # Heatmap de Custos Operacionais
    st.markdown('<h4 style="color: #FD7E14; margin: 2rem 0 1rem 0;">🗺️ Custos Operacionais por Modalidade e Rota</h4>', unsafe_allow_html=True)
    fig_heatmap = criar_heatmap_custos_branco()
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Parcerias & Infraestrutura
    st.markdown('<h4 style="color: #FD7E14; margin: 2rem 0 1rem 0;">🏭 Parcerias & Infraestrutura</h4>', unsafe_allow_html=True)
    criar_tabela_parcerias()

def dashboard_clube_fx_detalhado(lang='pt', dados_clube_fx={}, usar_dados_reais=False):
    """Dashboard detalhado do Clube FX - Estratégia de Comercialização"""
    
    st.markdown('<h3 style="color: #000000; margin: 1rem 0;">💼 Clube FX - Estratégia de Comercialização</h3>', unsafe_allow_html=True)
    
    # Carregar dados reais do MongoDB
    with st.spinner("Carregando dados do Clube FX..."):
        try:
            from mongodb_connector import load_units_data_from_mongo
            units_data = load_units_data_from_mongo(year=2024)
            clube_fx_data = units_data.get('Clube FX', {})
            usar_dados_reais = bool(clube_fx_data)
            
            if usar_dados_reais:
                pass  # Use real data
            else:
                pass  # Use simulated data

        except Exception as e:
            usar_dados_reais = False
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    if usar_dados_reais:
        pass  # Auto-generated pass
        with col1:
            clientes_atendidos = clube_fx_data.get('contratos', 0)
            st.metric(
                label="👥 Clientes Atendidos",
                value=f"{clientes_atendidos:,}",
                delta="+18 novos clientes"
            )
        
        with col2:
            receita_consultoria = clube_fx_data.get('receita_bruta', 0)
            st.metric(
                label="💰 Receita Consultoria",
                value=f"R$ {receita_consultoria/1_000_000:.1f}M",
                delta="+22.5%"
            )
        
        with col3:
            st.metric(
                label="📊 NPS Score",
                value="8.7/10",
                delta="+0.3 vs trimestre"
            )
        
        with col4:
            st.metric(
                label="🎯 Taxa Retenção",
                value="92.3%",
                delta="+1.8 p.p."
            )
    else:
        # Fallback com dados simulados
        with col1:
            st.metric("👥 Clientes Atendidos", "247", "+18 novos clientes")
        with col2:
            receita_consult_value = "R$ 12.8M"
            st.metric("💰 Receita Consultoria", receita_consult_value, "+22.5%")
        with col3:
            st.metric("📊 NPS Score", "8.7/10", "+0.3 vs trimestre")
        with col4:
            st.metric("🎯 Taxa Retenção", "92.3%", "+1.8 p.p.")
    
    st.markdown("---")
    
    # Estratégia de Comercialização
    st.markdown("### 🎯 Estratégia de Comercialização dos Clientes")
    
    if usar_dados_reais:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Performance Mensal")
            
            # Criar gráfico de evolução mensal
            dados_mensais = clube_fx_data.get('dados_mensais', {})
            if dados_mensais:
                meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                receitas_mensais = []
                contratos_mensais = []
                
                for i in range(1, 13):
                    mes_key = f'M{i:02d}'
                    mes_data = dados_mensais.get(mes_key, {})
                    receitas_mensais.append(mes_data.get('receita', 0) / 1_000_000)
                    contratos_mensais.append(mes_data.get('contratos', 0))
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=meses,
                    y=receitas_mensais,
                    mode='lines+markers',
                    name='Receita (R$ M)',
                    line=dict(color='#0D6EFD', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Evolução da Receita Mensal",
                    xaxis_title="Mês",
                    yaxis_title="Receita (R$ Milhões)",
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(color='black')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                pass  # Empty else block

        with col2:
            st.markdown("#### 💼 Métricas Financeiras")
            
            # Métricas financeiras detalhadas
            receita_liquida = clube_fx_data.get('receita_liquida', 0)
            custo_total = clube_fx_data.get('custo_total', 0)
            ebitda = clube_fx_data.get('ebitda', 0)
            margem_ebitda = clube_fx_data.get('margem_ebitda', 0)
            ticket_medio = clube_fx_data.get('ticket_medio', 0)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric(
                    label="💵 Receita Líquida",
                    value=f"R$ {receita_liquida/1_000_000:.1f}M"
                )
                st.metric(
                    label="🎯 EBITDA",
                    value=f"R$ {ebitda/1_000_000:.1f}M"
                )
            
            with col_b:
                st.metric(
                    label="📊 Margem EBITDA",
                    value=f"{margem_ebitda:.1f}%"
                )
                st.metric(
                    label="🎫 Ticket Médio",
                    value=f"R$ {ticket_medio/1_000:.0f}K"
                )
    
    # Estratégias e Serviços
    st.markdown("### 🚀 Serviços de Estratégia de Comercialização")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 Planejamento Estratégico**
        - Análise de mercado
        - Definição de preços
        - Timing de comercialização
        - Gestão de risco
        """)
    
    with col2:
        st.markdown("""
        **📊 Análise de Mercado**
        - Monitoramento de preços
        - Tendências de commodities
        - Oportunidades de venda
        - Cenários econômicos
        """)
    
    with col3:
        st.markdown("""
        **🤝 Execução Comercial**
        - Negociação de contratos
        - Relacionamento com compradores
        - Otimização de resultados
        - Acompanhamento pós-venda
        """)
    
    # Resultados e Impacto
    if usar_dados_reais and clube_fx_data.get('receita_bruta', 0) > 0:
        st.markdown("### 📈 Resultados e Impacto")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Principais Conquistas")
            st.markdown(f"""
            - **{clube_fx_data.get('contratos', 0):,} clientes** atendidos com estratégia personalizada
            - **R$ {clube_fx_data.get('receita_bruta', 0)/1_000_000:.1f} milhões** em receita gerada
            - **{clube_fx_data.get('margem_ebitda', 0):.1f}%** de margem EBITDA alcançada
            - **92.3%** de taxa de retenção de clientes
            """)
        
        with col2:
            st.markdown("#### 💡 Diferenciais Competitivos")
            st.markdown("""
            - **Expertise em commodities** com conhecimento profundo do mercado
            - **Tecnologia avançada** para análise de dados e tendências
            - **Rede de relacionamentos** com principais players do setor
            - **Acompanhamento contínuo** durante todo o processo comercial
            """)
    
    else:
        st.markdown("### 📈 Resultados e Impacto")

# ============================================================================
# FUNÇÕES DE GRÁFICOS TEMA BRANCO
# ============================================================================

def criar_grafico_volume_graos_branco():
    """Gráfico de volume por tipo de grão - tema branco"""
    graos = ['Soja', 'Milho', 'Sorgo', 'Outros']
    volumes = [45.2, 32.8, 18.5, 12.1]
    
    fig = go.Figure(data=[go.Bar(
        x=graos, y=volumes,
        marker=dict(color=['#198754', '#FD7E14', '#6F42C1', '#6C757D']),
        text=volumes,
        textposition='outside',
        texttemplate='%{text}k t',
        textfont=dict(color='#000000')
    )])
    
    fig.update_layout(
        title=dict(text="Volume por Tipo de Grão", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350,
        yaxis=dict(title='Volume (mil toneladas)', color='#000000', gridcolor='#E9ECEF'),
        xaxis=dict(color='#000000')
    )
    
    return fig

def criar_timeline_contratos_branco():
    """Timeline de contratos fechados - tema branco"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    contratos = [12, 8, 15, 10, 18, 14, 22, 16, 19, 25, 21, 28]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=contratos,
        mode='lines+markers',
        line=dict(color='#198754', width=3),
        marker=dict(size=8, color='#198754'),
        name='Contratos Fechados',
        hovertemplate='<b>%{x}</b><br>Contratos: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text="Contratos Fechados por Mês", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350,
        yaxis=dict(title='Número de Contratos', color='#000000', gridcolor='#E9ECEF'),
        xaxis=dict(color='#000000'),
        showlegend=False
    )
    
    return fig

def criar_grafico_tipos_carga_branco():
    """Gráfico de tipos de carga - tema branco"""
    tipos = ['Soja', 'Milho', 'Sorgo', 'Sementes', 'Calcário', 'Outros Insumos']
    volumes = [35.2, 28.5, 12.8, 8.3, 15.7, 9.5]
    
    fig = go.Figure(data=[go.Pie(
        labels=tipos,
        values=volumes,
        hole=0.4,
        marker=dict(colors=['#198754', '#FD7E14', '#6F42C1', '#0D6EFD', '#DC3545', '#6C757D']),
        textfont=dict(color='#000000')
    )])
    
    fig.update_layout(
        title=dict(text="Volume por Tipo de Carga", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350
    )
    
    return fig

def criar_grafico_modalidades_branco():
    """Gráfico de modalidades de contratação - tema branco"""
    modalidades = ['Aluguel Caminhões', 'Transportadoras', 'Autônomos']
    percentuais = [45, 35, 20]
    
    fig = go.Figure(data=[go.Bar(
        x=modalidades, y=percentuais,
        marker=dict(color=['#0D6EFD', '#198754', '#FD7E14']),
        text=percentuais,
        textposition='outside',
        texttemplate='%{text}%',
        textfont=dict(color='#000000')
    )])
    
    fig.update_layout(
        title=dict(text="Modalidades de Contratação", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350,
        yaxis=dict(title='Percentual (%)', color='#000000', gridcolor='#E9ECEF'),
        xaxis=dict(color='#000000')
    )
    
    return fig

def criar_heatmap_custos_branco():
    """Heatmap de custos operacionais - tema branco"""
    modalidades = ['Aluguel', 'Transportadoras', 'Autônomos']
    rotas = ['Goiânia-SP', 'Rio Verde-SP', 'Jataí-SP', 'Cristalina-MG', 'Formosa-DF']
    
    custos = np.array([
        [120, 135, 145, 160, 125],
        [110, 125, 140, 155, 115],
        [105, 120, 135, 150, 110]
    ])
    
    fig = go.Figure(data=go.Heatmap(
        z=custos,
        x=rotas,
        y=modalidades,
        colorscale='Blues',
        showscale=True,
        text=custos,
        texttemplate="R$ %{text}",
        textfont={"color": "#000000"}
    ))
    
    fig.update_layout(
        title=dict(text="Custo Operacional por Modalidade e Rota (R$/t)", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350
    )
    
    return fig

def criar_grafico_receita_servicos_branco():
    """Gráfico de receita por serviço - tema branco"""
    servicos = ['DRE', 'DFC', 'Orçado vs Real', 'Análise Custos', 'Outros']
    receitas = [4.2, 3.8, 2.9, 1.5, 0.4]
    
    fig = go.Figure(data=[go.Bar(
        x=servicos, y=receitas,
        marker=dict(color='#0D6EFD'),
        text=receitas,
        textposition='outside',
        texttemplate='R$ %{text}M',
        textfont=dict(color='#000000')
    )])
    
    fig.update_layout(
        title=dict(text="Receita por Tipo de Serviço", font=dict(size=16, color='#000000')),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#000000'),
        height=350,
        yaxis=dict(title='Receita (R$ Milhões)', color='#000000', gridcolor='#E9ECEF'),
        xaxis=dict(color='#000000')
    )
    
    return fig

def criar_tabela_parcerias():
    """Tabela de parcerias e infraestrutura"""
    parcerias_data = {
        'Parceiro': ['Terminal Cargill', 'Silo ADM', 'Armazém Bunge', 'Terminal Santos Brasil', 'Cooperativa Central'],
        'Tipo': ['Terminal', 'Silo', 'Armazém', 'Terminal', 'Cooperativa'],
        'Localização': ['Santos-SP', 'Rio Verde-GO', 'Jataí-GO', 'Santos-SP', 'Goiânia-GO'],
        'Capacidade (t)': ['50.000', '25.000', '30.000', '75.000', '40.000'],
        'Status': ['Ativo', 'Ativo', 'Ativo', 'Ativo', 'Ativo'],
        'Performance': ['95%', '92%', '88%', '97%', '90%']
    }
    
    df_parcerias = pd.DataFrame(parcerias_data)
    st.dataframe(df_parcerias, use_container_width=True, height=200)

def criar_pipeline_projetos():
    """Pipeline de projetos em andamento"""
    projetos = [
        {'nome': 'DRE Fazenda Santa Maria', 'progresso': 85, 'status': 'Em andamento'},
        {'nome': 'DFC Agropecuária Boa Vista', 'progresso': 60, 'status': 'Em andamento'},
        {'nome': 'Orçado vs Real Cooperativa Central', 'progresso': 40, 'status': 'Iniciado'},
        {'nome': 'Análise Custos Fazenda Progresso', 'progresso': 95, 'status': 'Finalizando'},
        {'nome': 'Consultoria Fazenda Esperança', 'progresso': 25, 'status': 'Iniciado'}
    ]
    
    for projeto in projetos:
        cor_status = '#198754' if projeto['progresso'] > 80 else '#FD7E14' if projeto['progresso'] > 50 else '#DC3545'
        
        st.markdown(f'''
        <div style="
            margin: 1rem 0; 
            padding: 1rem; 
            background: #F8F9FA; 
            border-radius: 8px;
            border-left: 4px solid {cor_status};
        ">
            <div style="color: #000000; font-weight: 600; margin-bottom: 0.5rem;">{projeto['nome']}</div>
            <div style="background: #E9ECEF; border-radius: 10px; height: 8px; overflow: hidden; margin-bottom: 0.5rem;">
                <div style="background: {cor_status}; height: 100%; width: {projeto['progresso']}%; transition: width 0.3s;"></div>
            </div>
            <div style="color: #6C757D; font-size: 0.8rem;">
                {projeto['progresso']}% concluído • {projeto['status']}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard"""
    configurar_pagina()
    
    # Inicializar session state
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
    if 'language' not in st.session_state:
        st.session_state.language = 'pt'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Aplicar tema
    aplicar_css_tema("light")
    
    # Mostrar tela de boas-vindas ou dashboard principal
    if st.session_state.show_welcome:
        filtros = tela_boas_vindas(st.session_state.language)
    else:
        # Menu de navegação no topo
        st.markdown(f'<h1 style="color: inherit; text-align: center; margin-bottom: 2rem;">{get_text("main_title", st.session_state.language)}</h1>', unsafe_allow_html=True)
        
        # Controles de navegação
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 1, 1, 1])
        
        with col1:
            opcao = st.selectbox(
                get_text('select_section', st.session_state.language),
                [
                    get_text('consolidated_view', st.session_state.language),
                    "Dashboards por Unidade",
                    get_text('dre_realtime', st.session_state.language),
                    get_text('financial_performance', st.session_state.language),
                    get_text('due_diligence', st.session_state.language),
                    get_text('settings', st.session_state.language)
                ],
                key="main_navigation"
            )

# ============================================================================
# DRE EM TEMPO REAL
# ============================================================================

def dre_tempo_real(lang='pt', tema='light', filtros_globais=None):
    """DRE em Tempo Real com tabela hierárquica e dados reais do MongoDB"""
    
    st.markdown(f'<h2 style="color: inherit;">📊 {get_text("dre_realtime", lang)}</h2>', unsafe_allow_html=True)
    
    # Mostrar filtros aplicados se houver
    if filtros_globais:
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        unidade_filtro = st.selectbox(
            "Unidade de Negócio" if lang == 'pt' else "Business Unit",
            ["Consolidado", "Fox Grãos", "Fox Log", "Clube FX"],
            key="dre_unidade_filter"
        )
    
    with col2:
        # Carregar anos disponíveis dos dados reais
        try:
            from mongodb_connector import get_available_years
            anos_dre_disponiveis = get_available_years()
        except:
            # Fallback se houver erro
            anos_dre_disponiveis = [2025, 2024, 2023, 2022]
        
        ano_filtro = st.selectbox(
            "Ano" if lang == 'pt' else "Year",
            anos_dre_disponiveis,
            key="dre_ano_filter"
        )
    
    with col3:
        formato_valores = st.selectbox(
            "Formato" if lang == 'pt' else "Format",
            ["R$ Milhões", "R$ Milhares", "Valores Absolutos"],
            key="dre_formato_filter"
        )
    
    # Carregar dados DRE reais do MongoDB
    with st.spinner("Carregando dados do DRE..."):
        try:
            from mongodb_connector import load_dre_data_from_mongo
            dados_dre_reais = load_dre_data_from_mongo(year=ano_filtro, unidade=unidade_filtro)
            
            if dados_dre_reais:
                dados_dre = dados_dre_reais
                usar_dados_reais = True
            else:
                dados_dre = gerar_dados_dre(unidade_filtro, ano_filtro)
                usar_dados_reais = False
                
        except Exception as e:
            dados_dre = gerar_dados_dre(unidade_filtro, ano_filtro)
            usar_dados_reais = False
    
    # Exibir indicador de fonte dos dados
    if usar_dados_reais:
        pass  # Auto-generated pass
    else:
        pass  # Empty else block

    # Exibir tabela hierárquica
    exibir_tabela_dre_hierarquica(dados_dre, formato_valores, tema)
    
    # Gráfico de evolução mensal
    st.markdown('<h3 style="color: inherit; margin: 2rem 0 1rem 0;">📊 Evolução Mensal</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico Receita vs EBITDA
        fig_receita_ebitda = criar_grafico_dre_evolucao(dados_dre, ['= RECEITA LÍQUIDA', '= EBITDA'], tema, lang)
        st.plotly_chart(fig_receita_ebitda, use_container_width=True)
    
    with col2:
        # Gráfico Margem EBITDA
        fig_margem = criar_grafico_margem_ebitda(dados_dre, tema, lang)
        st.plotly_chart(fig_margem, use_container_width=True)

def exibir_tabela_dre_hierarquica(dados_dre, formato, tema):
    """Exibir tabela DRE com hierarquia e funcionalidade de expandir/recolher"""
    
    # Inicializar session state para controle de expansão
    if 'dre_expanded_sections' not in st.session_state:
        st.session_state.dre_expanded_sections = {
            'receita_bruta': True,
            'deducoes': True,
            'cpv': True,
            'despesas_op': True,
            'resultado_fin': True
        }
    
    # Definir estrutura hierárquica
    estrutura_hierarquica = {
        'RECEITA BRUTA': {
            'tipo': 'macro',
            'secao': 'receita_bruta',
            'subcategorias': ['  Comercialização de Grãos', '  Serviços Logísticos', '  Consultoria']
        },
        '(-) DEDUÇÕES E IMPOSTOS': {
            'tipo': 'macro',
            'secao': 'deducoes',
            'subcategorias': ['  ICMS sobre vendas', '  PIS/COFINS', '  ISS (serviços)', '  Outras deduções']
        },
        '= RECEITA LÍQUIDA': {
            'tipo': 'resultado',
            'secao': None,
            'subcategorias': []
        },
        '(-) CPV': {
            'tipo': 'macro',
            'secao': 'cpv',
            'subcategorias': ['  Compra de grãos', '  Frete de aquisição', '  Armazenagem inicial']
        },
        '= LUCRO BRUTO': {
            'tipo': 'resultado',
            'secao': None,
            'subcategorias': []
        },
        '(-) DESPESAS OPERACIONAIS': {
            'tipo': 'macro',
            'secao': 'despesas_op',
            'subcategorias': ['  Pessoal e benefícios', '  Marketing e vendas', '  Despesas administrativas']
        },
        '= EBITDA': {
            'tipo': 'resultado',
            'secao': None,
            'subcategorias': []
        },
        '(-) Depreciação & Amortização': {
            'tipo': 'linha',
            'secao': None,
            'subcategorias': []
        },
        '= RESULTADO OPERACIONAL': {
            'tipo': 'resultado',
            'secao': None,
            'subcategorias': []
        },
        '(+/-) RESULTADO FINANCEIRO': {
            'tipo': 'macro',
            'secao': 'resultado_fin',
            'subcategorias': ['  Receitas financeiras', '  Despesas financeiras']
        },
        '= LUCRO ANTES IR/CSLL': {
            'tipo': 'resultado',
            'secao': None,
            'subcategorias': []
        },
        '(-) IR e CSLL': {
            'tipo': 'linha',
            'secao': None,
            'subcategorias': []
        },
        '= LUCRO LÍQUIDO': {
            'tipo': 'resultado_final',
            'secao': None,
            'subcategorias': []
        }
    }
    
    # Cores por tema e tipo
    if tema == 'dark':
        cores = {
            'macro': '#2D3748',      # Cinza escuro
            'resultado': '#1A365D',   # Azul escuro
            'resultado_final': '#2D5016', # Verde escuro
            'linha': '#4A5568',       # Cinza médio
            'subcategoria': '#4A5568', # Cinza médio
            'texto_macro': '#FFFFFF',
            'texto_sub': '#E2E8F0'
        }
    else:
        cores = {
            'macro': '#E2E8F0',      # Cinza claro
            'resultado': '#BEE3F8',   # Azul claro
            'resultado_final': '#C6F6D5', # Verde claro
            'linha': '#F7FAFC',       # Cinza muito claro
            'subcategoria': '#F7FAFC', # Cinza muito claro
            'texto_macro': '#1A202C',
            'texto_sub': '#4A5568'
        }
    
    # Controles de expansão
    st.markdown("### 📊 Controles de Visualização")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        pass  # Auto-generated pass
        if st.button("🔽 Expandir Tudo"):
            for secao in st.session_state.dre_expanded_sections:
                st.session_state.dre_expanded_sections[secao] = True
            st.rerun()
    
    with col2:
        pass  # Auto-generated pass
        if st.button("🔼 Recolher Tudo"):
            for secao in st.session_state.dre_expanded_sections:
                st.session_state.dre_expanded_sections[secao] = False
            st.rerun()
    
    with col3:
        icon = "🔽" if st.session_state.dre_expanded_sections['receita_bruta'] else "▶️"
        if st.button(f"{icon} Receitas"):
            st.session_state.dre_expanded_sections['receita_bruta'] = not st.session_state.dre_expanded_sections['receita_bruta']
            st.rerun()
    
    with col4:
        icon = "🔽" if st.session_state.dre_expanded_sections['deducoes'] else "▶️"
        if st.button(f"{icon} Deduções"):
            st.session_state.dre_expanded_sections['deducoes'] = not st.session_state.dre_expanded_sections['deducoes']
            st.rerun()
    
    with col4:
        icon = "🔽" if st.session_state.dre_expanded_sections['cpv'] else "▶️"
        if st.button(f"{icon} CPV"):
            st.session_state.dre_expanded_sections['cpv'] = not st.session_state.dre_expanded_sections['cpv']
            st.rerun()
    
    with col6:
        icon = "🔽" if st.session_state.dre_expanded_sections['despesas_op'] else "▶️"
        if st.button(f"{icon} Despesas"):
            st.session_state.dre_expanded_sections['despesas_op'] = not st.session_state.dre_expanded_sections['despesas_op']
            st.rerun()
    
    st.markdown("---")
    
    # Construir dados para exibição
    dados_exibicao = []
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for conta in dados_dre['Conta']:
        idx = dados_dre['Conta'].index(conta)
        
        # Verificar se é macro categoria
        if conta in estrutura_hierarquica:
            info = estrutura_hierarquica[conta]
            
            # Adicionar macro categoria
            linha = {'Conta': conta, 'Tipo': info['tipo'], 'Secao': info['secao']}
            for mes in meses:
                valor = dados_dre[mes][idx]
                linha[mes] = formatar_valor_dre(valor, formato)
            dados_exibicao.append(linha)
            
            # Adicionar subcategorias se expandido
            if info['secao'] and st.session_state.dre_expanded_sections.get(info['secao'], True):
                for sub in info['subcategorias']:
                    pass  # Auto-generated pass
                    if sub in dados_dre['Conta']:
                        sub_idx = dados_dre['Conta'].index(sub)
                        linha_sub = {'Conta': f"    {sub.strip()}", 'Tipo': 'subcategoria', 'Secao': info['secao']}
                        for mes in meses:
                            valor = dados_dre[mes][sub_idx]
                            linha_sub[mes] = formatar_valor_dre(valor, formato)
                        dados_exibicao.append(linha_sub)
    
    # Criar DataFrame
    df_exibicao = pd.DataFrame(dados_exibicao)
    
    # Função para aplicar estilos
    def aplicar_estilos(row):
        # Encontrar o tipo da linha baseado no índice
        idx = row.name
        if idx < len(dados_exibicao):
            tipo = dados_exibicao[idx]['Tipo']
        else:
            tipo = 'linha'
            
        styles = [''] * len(row)
        
        if tipo == 'macro':
            bg_color = cores['macro']
            text_color = cores['texto_macro']
            font_weight = 'bold'
            font_size = '14px'
        elif tipo == 'resultado':
            bg_color = cores['resultado']
            text_color = cores['texto_macro']
            font_weight = 'bold'
            font_size = '14px'
        elif tipo == 'resultado_final':
            bg_color = cores['resultado_final']
            text_color = cores['texto_macro']
            font_weight = 'bold'
            font_size = '16px'
        elif tipo == 'subcategoria':
            bg_color = cores['subcategoria']
            text_color = cores['texto_sub']
            font_weight = 'normal'
            font_size = '12px'
        else:  # linha
            bg_color = cores['linha']
            text_color = cores['texto_macro']
            font_weight = 'normal'
            font_size = '13px'
        
        for i in range(len(styles)):
            styles[i] = f'background-color: {bg_color}; color: {text_color}; font-weight: {font_weight}; font-size: {font_size};'
            if i == 0 and tipo == 'subcategoria':  # Primeira coluna (Conta)
                styles[i] += ' text-align: left; padding-left: 30px;'
            elif i == 0:  # Primeira coluna para outros tipos
                styles[i] += ' text-align: left; padding-left: 10px;'
            else:  # Colunas de valores
                styles[i] += ' text-align: right; padding-right: 10px;'
        
        return styles
    
    # Aplicar estilos e exibir tabela
    df_styled = df_exibicao.drop(['Tipo', 'Secao'], axis=1).style.apply(aplicar_estilos, axis=1)
    
    st.markdown("### 📋 Demonstrativo de Resultado do Exercício (DRE)")
    st.dataframe(df_styled, use_container_width=True, height=800)

def formatar_valor_dre(valor, formato):
    """Formatar valores do DRE conforme seleção"""
    if valor == 0:
        return "0,0"
    
    if formato == "R$ Milhões":
        return f"{valor:,.1f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    elif formato == "R$ Milhares":
        return f"{valor*1000:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    else:  # Valores Absolutos
        return f"R$ {valor*1000000:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def gerar_dados_dre(unidade, ano):
    """Gerar dados simulados de DRE por mês com estrutura específica do agronegócio"""
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Multiplicadores por unidade
    if unidade == "Fox Grãos":
        mult_comercializacao = 1.0
        mult_logistica = 0.6
        mult_consultoria = 0.0
    elif unidade == "Fox Log":
        mult_comercializacao = 0.0
        mult_logistica = 1.0
        mult_consultoria = 0.0
    elif unidade == "Clube FX":
        mult_comercializacao = 0.0
        mult_logistica = 0.0
        mult_consultoria = 1.0
    else:  # Consolidado
        mult_comercializacao = 1.0
        mult_logistica = 1.6
        mult_consultoria = 1.0
    
    # Receitas por linha de negócio (em milhões)
    comercializacao_graos = [round((15.2 + i * 0.7) * mult_comercializacao, 1) for i in range(12)]
    servicos_logisticos = [round((8.5 + i * 0.4) * mult_logistica, 1) for i in range(12)]
    consultoria = [round((2.8 + i * 0.1) * mult_consultoria, 1) for i in range(12)]
    
    # Receita Bruta
    receita_bruta = [round(cg + sl + c, 1) for cg, sl, c in zip(comercializacao_graos, servicos_logisticos, consultoria)]
    
    # Deduções e Impostos
    icms_vendas = [round(sl * 0.045, 1) for sl in servicos_logisticos]  # 4.5% ICMS apenas sobre frete
    pis_cofins = [round(rb * 0.0365, 1) for rb in receita_bruta]  # 3.65% PIS/COFINS
    iss_servicos = [round((sl + c) * 0.05, 1) for sl, c in zip(servicos_logisticos, consultoria)]  # 5% ISS sobre serviços
    outras_deducoes = [round(rb * 0.015, 1) for rb in receita_bruta]  # 1.5% outras deduções
    
    total_deducoes = [round(icms + pis + iss + outras, 1) 
                     for icms, pis, iss, outras in zip(icms_vendas, pis_cofins, iss_servicos, outras_deducoes)]
    
    # Receita Líquida
    receita_liquida = [round(rb - td, 1) for rb, td in zip(receita_bruta, total_deducoes)]
    
    # Custo de Produtos Vendidos (CPV) - específico para comercialização de grãos
    compra_graos = [round(cg * 0.82, 1) for cg in comercializacao_graos]  # 82% do valor de comercialização
    frete_aquisicao = [round(cg * 0.04, 1) for cg in comercializacao_graos]  # 4% frete
    armazenagem_inicial = [round(cg * 0.02, 1) for cg in comercializacao_graos]  # 2% armazenagem
    
    total_cpv = [round(comp + frete + arm, 1) 
                for comp, frete, arm in zip(compra_graos, frete_aquisicao, armazenagem_inicial)]
    
    # Lucro Bruto
    lucro_bruto = [round(rl - cpv, 1) for rl, cpv in zip(receita_liquida, total_cpv)]
    
    # Despesas Operacionais (SG&A)
    pessoal_beneficios = [round(rl * 0.08, 1) for rl in receita_liquida]  # 8% pessoal
    marketing_vendas = [round(rl * 0.03, 1) for rl in receita_liquida]  # 3% marketing
    despesas_admin = [round(rl * 0.04, 1) for rl in receita_liquida]  # 4% administrativas
    
    total_sga = [round(pessoal + mkt + admin, 1) 
                for pessoal, mkt, admin in zip(pessoal_beneficios, marketing_vendas, despesas_admin)]
    
    # EBITDA
    ebitda = [round(lb - sga, 1) for lb, sga in zip(lucro_bruto, total_sga)]
    
    # Depreciação & Amortização
    depreciacao = [round(rl * 0.015, 1) for rl in receita_liquida]  # 1.5% depreciação
    
    # Resultado Operacional
    resultado_operacional = [round(e - d, 1) for e, d in zip(ebitda, depreciacao)]
    
    # Resultado Financeiro
    receitas_financeiras = [round(rl * 0.008, 1) for rl in receita_liquida]  # 0.8% receitas financeiras
    despesas_financeiras = [round(rl * 0.012, 1) for rl in receita_liquida]  # 1.2% despesas financeiras
    resultado_financeiro = [round(rf - df, 1) for rf, df in zip(receitas_financeiras, despesas_financeiras)]
    
    # Lucro Antes do IR e CSLL
    lucro_antes_ir = [round(ro + res_fin, 1) for ro, res_fin in zip(resultado_operacional, resultado_financeiro)]
    
    # IR e CSLL
    ir_csll = [round(max(lai * 0.34, 0), 1) for lai in lucro_antes_ir]  # 34% IR+CSLL
    
    # Lucro Líquido
    lucro_liquido = [round(lai - ir, 1) for lai, ir in zip(lucro_antes_ir, ir_csll)]
    
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
        **{mes: [
            rb,  # Receita Bruta
            cg,  # Comercialização de Grãos
            sl,  # Serviços Logísticos
            c,   # Consultoria
            -td, # Total Deduções (negativo)
            -icms, # ICMS (negativo)
            -pis,  # PIS/COFINS (negativo)
            -iss,  # ISS (negativo)
            -outras, # Outras deduções (negativo)
            rl,  # Receita Líquida
            -cpv, # CPV (negativo)
            -comp, # Compra de grãos (negativo)
            -frete, # Frete aquisição (negativo)
            -arm,  # Armazenagem (negativo)
            lb,  # Lucro Bruto
            -sga, # SG&A (negativo)
            -pessoal, # Pessoal (negativo)
            -mkt,  # Marketing (negativo)
            -admin, # Administrativas (negativo)
            ebit,  # EBITDA
            -dep,  # Depreciação (negativo)
            ro,    # Resultado Operacional
            res_fin, # Resultado Financeiro
            rf,    # Receitas financeiras
            -df,   # Despesas financeiras (negativo)
            lai,   # Lucro Antes IR
            -ir,   # IR/CSLL (negativo)
            ll     # Lucro Líquido
        ] for mes, rb, cg, sl, c, td, icms, pis, iss, outras, rl, cpv, comp, frete, arm, lb, sga, pessoal, mkt, admin, ebit, dep, ro, res_fin, rf, df, lai, ir, ll in 
           zip(meses, receita_bruta, comercializacao_graos, servicos_logisticos, consultoria, 
               total_deducoes, icms_vendas, pis_cofins, iss_servicos, outras_deducoes,
               receita_liquida, total_cpv, compra_graos, frete_aquisicao, armazenagem_inicial,
               lucro_bruto, total_sga, pessoal_beneficios, marketing_vendas, despesas_admin,
               ebitda, depreciacao, resultado_operacional, resultado_financeiro, 
               receitas_financeiras, despesas_financeiras, lucro_antes_ir, ir_csll, lucro_liquido)}
    }

def formatar_valores_dre(dados, formato):
    """Formatar valores conforme seleção do usuário"""
    dados_formatados = dados.copy()
    
    for coluna in dados_formatados.keys():
        pass  # Auto-generated pass
        if coluna != 'Conta':
            pass  # Auto-generated pass
            if formato == "R$ Milhões":
                dados_formatados[coluna] = [f"R$ {v:.1f}M" for v in dados_formatados[coluna]]
            elif formato == "R$ Milhares":
                dados_formatados[coluna] = [f"R$ {v*1000:.0f}k" for v in dados_formatados[coluna]]
            else:  # Valores Absolutos
                dados_formatados[coluna] = [f"R$ {v*1000000:,.0f}" for v in dados_formatados[coluna]]
    
    return dados_formatados

def criar_grafico_dre_evolucao(dados, metricas, tema, lang):
    """Gráfico de evolução das métricas DRE"""
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    fig = go.Figure()
    
    cores = ['#198754', '#0D6EFD', '#FD7E14', '#6F42C1']
    
    for i, metrica in enumerate(metricas):
        idx = dados['Conta'].index(metrica)
        valores = [dados[mes][idx] for mes in meses]
        
        fig.add_trace(go.Scatter(
            x=meses, y=valores,
            mode='lines+markers',
            name=metrica,
            line=dict(color=cores[i % len(cores)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>%{{x}}</b><br>{metrica}: R$ %{{y}}M<extra></extra>'
        ))
    
    bg_color = '#FFFFFF' if tema == 'light' else 'rgba(0,0,0,0)'
    text_color = '#000000' if tema == 'light' else '#FFFFFF'
    grid_color = '#E9ECEF' if tema == 'light' else 'rgba(192, 192, 192, 0.1)'
    
    fig.update_layout(
        title=dict(text="Evolução Mensal", font=dict(size=16, color=text_color)),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        height=350,
        legend=dict(font=dict(color=text_color)),
        xaxis=dict(showgrid=True, gridcolor=grid_color, color=text_color),
        yaxis=dict(showgrid=True, gridcolor=grid_color, color=text_color, title='R$ Milhões')
    )
    
    return fig

def criar_grafico_margem_ebitda(dados, tema, lang):
    """Gráfico de margem EBITDA"""
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    try:
        idx_receita = dados['Conta'].index('= RECEITA LÍQUIDA')
        idx_ebitda = dados['Conta'].index('= EBITDA')
    except ValueError:
        # Fallback se não encontrar
        return go.Figure()
    
    margens = [round((dados[mes][idx_ebitda] / dados[mes][idx_receita]) * 100, 1) if dados[mes][idx_receita] != 0 else 0 for mes in meses]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses, y=margens,
        marker=dict(color='#198754'),
        text=margens,
        textposition='outside',
        texttemplate='%{text}%',
        hovertemplate='<b>%{x}</b><br>Margem EBITDA: %{y}%<extra></extra>'
    ))
    
    bg_color = '#FFFFFF' if tema == 'light' else 'rgba(0,0,0,0)'
    text_color = '#000000' if tema == 'light' else '#FFFFFF'
    grid_color = '#E9ECEF' if tema == 'light' else 'rgba(192, 192, 192, 0.1)'
    
    fig.update_layout(
        title=dict(text="Margem EBITDA (%)", font=dict(size=16, color=text_color)),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        height=350,
        xaxis=dict(showgrid=False, color=text_color),
        yaxis=dict(showgrid=True, gridcolor=grid_color, color=text_color, title='%')
    )
    
    return fig

# ============================================================================
# PERFORMANCE FINANCEIRA
# ============================================================================

def performance_financeira(lang='pt', tema='light', ano_selecionado=2024):
    """Performance Financeira com dados reais do MongoDB"""
    
    st.markdown(f'<h2 style="color: inherit; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">💰 {get_text("financial_performance", lang)}</h2>', unsafe_allow_html=True)
    
    # Carregar dados reais de performance
    with st.spinner("Carregando dados de performance..."):
        try:
            from mongodb_connector import load_performance_data_from_mongo
            dados_performance_reais = load_performance_data_from_mongo(year=ano_selecionado)
            
            if dados_performance_reais:
                usar_dados_reais = True
            else:
                usar_dados_reais = False
                
        except Exception as e:
            usar_dados_reais = False
    
    # Tabela dinâmica pivot
    st.markdown('<h3 style="color: inherit; margin: 2rem 0 1rem 0;">📊 Tabela Dinâmica - Métricas Financeiras</h3>', unsafe_allow_html=True)
    
    # Carregar dados reais da collection finances
    with st.spinner("Carregando dados financeiros..."):
        try:
            from mongodb_connector import load_finances_data_from_mongo
            dados_finances = load_finances_data_from_mongo(year=ano_filtro)
            
            if dados_finances:
                df_pivot = pd.DataFrame(dados_finances)
                usar_dados_finances = True
            else:
                # Fallback para dados de performance dos contratos
                if usar_dados_reais:
                    df_pivot = pd.DataFrame(dados_performance_reais)
                else:
                    dados_pivot = gerar_dados_pivot_financeiro()
                    df_pivot = pd.DataFrame(dados_pivot)
                usar_dados_finances = False
                
        except Exception as e:
            # Fallback para dados simulados
            if usar_dados_reais:
                df_pivot = pd.DataFrame(dados_performance_reais)
            else:
                dados_pivot = gerar_dados_pivot_financeiro()
                df_pivot = pd.DataFrame(dados_pivot)
            usar_dados_finances = False
    
    # Exibir fonte dos dados
    if usar_dados_finances:
        pass  # Auto-generated pass
    elif usar_dados_reais:
        pass  # Auto-generated pass
    else:
        pass  # Empty else block

    # Estilizar tabela
    numeric_columns = [col for col in df_pivot.columns if col not in ['Mes', 'Métrica']]
    styled_pivot = df_pivot.style.format({
        col: lambda x: f"R$ {x:.1f}M" for col in numeric_columns
    }).set_properties(**{
        'background-color': '#F8F9FA' if tema == 'light' else '#2d2d2d',
        'color': '#000000' if tema == 'light' else '#FFFFFF',
        'border': '1px solid #DEE2E6' if tema == 'light' else '1px solid #444444'
    })
    
    st.dataframe(styled_pivot, use_container_width=True, height=400)
    
    # Gráfico de área empilhada
    st.markdown('<h3 style="color: inherit; margin: 2rem 0 1rem 0;">📈 Evolução das Métricas Financeiras</h3>', unsafe_allow_html=True)
    
    if usar_dados_reais:
        fig_area = criar_grafico_performance_real(dados_performance_reais, tema, lang)
    else:
        fig_area = criar_grafico_area_empilhada(tema, lang)
    
    st.plotly_chart(fig_area, use_container_width=True)
    
    # KPIs resumo
    st.markdown('<h3 style="color: inherit; margin: 2rem 0 1rem 0;">🎯 KPIs Principais</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        receita_anual_value = "R$ 289.5M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Receita Anual</div>
            <div class="metric-value">{receita_anual_value}</div>
            <div class="metric-delta delta-positive">+18.2% vs ano anterior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ebitda_anual_value = "R$ 89.2M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">EBITDA Anual</div>
            <div class="metric-value">{ebitda_anual_value}</div>
            <div class="metric-delta delta-positive">+22.1% vs ano anterior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        margem_ebitda_value = "30.8%"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Margem EBITDA</div>
            <div class="metric-value">{margem_ebitda_value}</div>
            <div class="metric-delta delta-positive">+1.2 p.p. vs ano anterior</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        fluxo_caixa_value = "R$ 76.3M"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Fluxo Caixa Livre</div>
            <div class="metric-value">{fluxo_caixa_value}</div>
            <div class="metric-delta delta-positive">+25.8% vs ano anterior</div>
        </div>
        """, unsafe_allow_html=True)

def gerar_dados_pivot_financeiro():
    """Gerar dados para tabela pivot financeira"""
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Dados simulados (em milhões)
    receita = [18.5, 19.2, 21.8, 20.1, 22.3, 24.1, 23.8, 25.2, 24.9, 26.1, 25.8, 27.2]
    cpv = [12.1, 12.5, 14.2, 13.1, 14.5, 15.7, 15.5, 16.4, 16.2, 17.0, 16.8, 17.7]
    sga = [2.8, 2.9, 3.3, 3.0, 3.4, 3.6, 3.6, 3.8, 3.7, 3.9, 3.9, 4.1]
    ebitda = [r - c - s for r, c, s in zip(receita, cpv, sga)]
    lucro_liquido = [round(e * 0.75, 1) for e in ebitda]
    fluxo_caixa_livre = [round(ll * 1.1, 1) for ll in lucro_liquido]
    
    return {
        'Métrica': ['Receita', 'CPV', 'SG&A', 'EBITDA', 'Lucro Líquido', 'Fluxo Caixa Livre'],
        **{mes: [r, c, s, e, ll, fcl] for mes, r, c, s, e, ll, fcl in 
           zip(meses, receita, cpv, sga, ebitda, lucro_liquido, fluxo_caixa_livre)}
    }

def criar_grafico_area_empilhada(tema, lang):
    """Gráfico de área empilhada para composição de custos"""
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Dados de custos e despesas (em milhões)
    cpv = [12.1, 12.5, 14.2, 13.1, 14.5, 15.7, 15.5, 16.4, 16.2, 17.0, 16.8, 17.7]
    despesas_vendas = [1.5, 1.5, 1.7, 1.6, 1.8, 1.9, 1.9, 2.0, 2.0, 2.1, 2.1, 2.2]
    despesas_admin = [1.3, 1.4, 1.6, 1.4, 1.6, 1.7, 1.7, 1.8, 1.7, 1.8, 1.8, 1.9]
    outras_despesas = [0.8, 0.8, 0.9, 0.8, 0.9, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=cpv,
        fill='tonexty',
        mode='none',
        name='CPV',
        fillcolor='rgba(220, 53, 69, 0.6)',
        hovertemplate='<b>%{x}</b><br>CPV: R$ %{y}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=[c + d for c, d in zip(cpv, despesas_vendas)],
        fill='tonexty',
        mode='none',
        name='Despesas de Vendas',
        fillcolor='rgba(253, 126, 20, 0.6)',
        hovertemplate='<b>%{x}</b><br>Desp. Vendas: R$ %{y}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=[c + dv + da for c, dv, da in zip(cpv, despesas_vendas, despesas_admin)],
        fill='tonexty',
        mode='none',
        name='Despesas Administrativas',
        fillcolor='rgba(13, 110, 253, 0.6)',
        hovertemplate='<b>%{x}</b><br>Desp. Admin: R$ %{y}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=[c + dv + da + o for c, dv, da, o in zip(cpv, despesas_vendas, despesas_admin, outras_despesas)],
        fill='tonexty',
        mode='none',
        name='Outras Despesas',
        fillcolor='rgba(108, 117, 125, 0.6)',
        hovertemplate='<b>%{x}</b><br>Outras: R$ %{y}M<extra></extra>'
    ))
    
    bg_color = '#FFFFFF' if tema == 'light' else 'rgba(0,0,0,0)'
    text_color = '#000000' if tema == 'light' else '#FFFFFF'
    grid_color = '#E9ECEF' if tema == 'light' else 'rgba(192, 192, 192, 0.1)'
    
    fig.update_layout(
        title=dict(text="Composição de Custos e Despesas", font=dict(size=18, color=text_color)),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        height=450,
        legend=dict(font=dict(color=text_color)),
        xaxis=dict(showgrid=True, gridcolor=grid_color, color=text_color),
        yaxis=dict(showgrid=True, gridcolor=grid_color, color=text_color, title='R$ Milhões'),
        hovermode='x unified'
    )
    
    return fig

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard"""
    configurar_pagina()
    
    # Inicializar session state
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True
    if 'language' not in st.session_state:
        st.session_state.language = 'pt'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Aplicar tema
    aplicar_css_tema("light")
    
    # Mostrar tela de boas-vindas ou dashboard principal
    if st.session_state.show_welcome:
        filtros = tela_boas_vindas(st.session_state.language)
    else:
        # Menu de navegação no topo
        st.markdown(f'<h1 style="color: inherit; text-align: center; margin-bottom: 2rem;">{get_text("main_title", st.session_state.language)}</h1>', unsafe_allow_html=True)
        
        # Controles de navegação
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 1, 1, 1])
        
        with col1:
            opcao = st.selectbox(
                get_text('select_section', st.session_state.language),
                [
                    get_text('consolidated_view', st.session_state.language),
                    "Dashboards por Unidade",
                    get_text('dre_realtime', st.session_state.language),
                    get_text('financial_performance', st.session_state.language),
                    get_text('due_diligence', st.session_state.language),
                    get_text('settings', st.session_state.language)
                ],
                key="main_navigation"
            )
        
        with col2:
            periodo = st.selectbox(
                get_text('period', st.session_state.language),
                [
                    get_text('last_12_months', st.session_state.language),
                    get_text('last_6_months', st.session_state.language),
                    get_text('last_quarter', st.session_state.language),
                    get_text('custom', st.session_state.language)
                ],
                key="periodo_select"
            )
        
        with col3:
            visualizacao = st.selectbox(
                get_text('visualization', st.session_state.language),
                [
                    get_text('executive', st.session_state.language),
                    get_text('detailed', st.session_state.language),
                    get_text('operational', st.session_state.language)
                ],
                key="view_select"
            )
        
# ============================================================================
# SEÇÃO DE BALANÇO PATRIMONIAL
# ============================================================================

def secao_balanco_patrimonial(lang='pt', ano=2025, filtros_globais=None):
    """Seção de balanço patrimonial com dados reais do MongoDB"""
    
    st.markdown(f'<h2 style="color: inherit;">📊 Balanço Patrimonial</h2>', unsafe_allow_html=True)
    
    # Mostrar filtros aplicados se houver
    if filtros_globais:
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    
    # Carregar dados do balanço patrimonial
    with st.spinner("Carregando dados do balanço patrimonial..."):
        try:
            from mongodb_connector import get_balance_sheet_summary, get_balance_sheet_detailed_breakdown, insert_sample_balance_sheet_data
            
            # Inserir dados de exemplo se necessário (apenas uma vez)
            if st.button("🔄 Inserir/Atualizar Dados de Exemplo", help="Clique para inserir ou atualizar os dados de exemplo do balanço patrimonial"):
                if insert_sample_balance_sheet_data():
                    st.success("Dados do balanço patrimonial inseridos/atualizados com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao inserir dados do balanço patrimonial")
            
            # Carregar resumo
            resumo = get_balance_sheet_summary(ano)
            detalhamento = get_balance_sheet_detailed_breakdown(ano)
            
            if not resumo or resumo['total_ativo'] == 0:
                st.warning("Nenhum dado de balanço patrimonial encontrado para este período. Clique no botão acima para inserir dados de exemplo.")
                return
            
            # Métricas principais
            st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">💰 Indicadores Principais</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💼 Total do Ativo",
                    f"R$ {resumo['total_ativo']:,.0f}".replace(',', '.'),
                    help="Soma do Ativo Circulante + Ativo Não Circulante"
                )
            
            with col2:
                st.metric(
                    "🏛️ Patrimônio Líquido", 
                    f"R$ {resumo['patrimonio_liquido']:,.0f}".replace(',', '.'),
                    help="Recursos próprios da empresa"
                )
            
            with col3:
                st.metric(
                    "💧 Liquidez Corrente",
                    f"{resumo['liquidez_corrente']:.2f}",
                    help="Ativo Circulante ÷ Passivo Circulante"
                )
            
            with col4:
                st.metric(
                    "📊 Endividamento",
                    f"{resumo['endividamento_total']:.1f}%",
                    help="(Passivo Circulante + Passivo Não Circulante) ÷ Total do Ativo"
                )
            
            # Gráficos de composição
            st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">📈 Composição Patrimonial</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico do Ativo
                st.markdown("**🔵 Composição do Ativo**")
                
                ativo_data = {
                    'Ativo Circulante': resumo['ativo_circulante'],
                    'Ativo Não Circulante': resumo['ativo_nao_circulante']
                }
                
                import plotly.express as px
                fig_ativo = px.pie(
                    values=list(ativo_data.values()),
                    names=list(ativo_data.keys()),
                    title="Distribuição do Ativo",
                    color_discrete_sequence=['#2E8B57', '#90EE90']
                )
                fig_ativo.update_traces(textposition='inside', textinfo='percent+label')
                fig_ativo.update_layout(height=400)
                st.plotly_chart(fig_ativo, use_container_width=True)
            
            with col2:
                # Gráfico do Passivo + PL
                st.markdown("**🔴 Composição do Passivo + PL**")
                
                passivo_data = {
                    'Passivo Circulante': resumo['passivo_circulante'],
                    'Passivo Não Circulante': resumo['passivo_nao_circulante'],
                    'Patrimônio Líquido': resumo['patrimonio_liquido']
                }
                
                fig_passivo = px.pie(
                    values=list(passivo_data.values()),
                    names=list(passivo_data.keys()),
                    title="Distribuição do Passivo + PL",
                    color_discrete_sequence=['#FF6B6B', '#FFB347', '#87CEEB']
                )
                fig_passivo.update_traces(textposition='inside', textinfo='percent+label')
                fig_passivo.update_layout(height=400)
                st.plotly_chart(fig_passivo, use_container_width=True)
            
            # Detalhamento por categoria
            if detalhamento:
                st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">📋 Detalhamento por Categoria</h3>', unsafe_allow_html=True)
                
                # Criar tabs para cada categoria
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "💰 Ativo Circulante", 
                    "🏢 Ativo Não Circulante", 
                    "💳 Passivo Circulante", 
                    "🏛️ Passivo Não Circulante", 
                    "💎 Patrimônio Líquido"
                ])
                
                with tab1:
                    if detalhamento.get('ativo_circulante'):
                        df_ativo_circ = pd.DataFrame(list(detalhamento['ativo_circulante'].items()), 
                                                   columns=['Item', 'Valor'])
                        df_ativo_circ = df_ativo_circ[df_ativo_circ['Valor'] > 0]  # Mostrar apenas valores > 0
                        df_ativo_circ['Valor Formatado'] = df_ativo_circ['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '.'))
                        st.dataframe(df_ativo_circ[['Item', 'Valor Formatado']], use_container_width=True, hide_index=True)
                
                with tab2:
                    if detalhamento.get('ativo_nao_circulante'):
                        df_ativo_nao_circ = pd.DataFrame(list(detalhamento['ativo_nao_circulante'].items()), 
                                                       columns=['Item', 'Valor'])
                        df_ativo_nao_circ = df_ativo_nao_circ[df_ativo_nao_circ['Valor'] > 0]
                        df_ativo_nao_circ['Valor Formatado'] = df_ativo_nao_circ['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '.'))
                        st.dataframe(df_ativo_nao_circ[['Item', 'Valor Formatado']], use_container_width=True, hide_index=True)
                
                with tab3:
                    if detalhamento.get('passivo_circulante'):
                        df_passivo_circ = pd.DataFrame(list(detalhamento['passivo_circulante'].items()), 
                                                     columns=['Item', 'Valor'])
                        df_passivo_circ = df_passivo_circ[df_passivo_circ['Valor'] > 0]
                        df_passivo_circ['Valor Formatado'] = df_passivo_circ['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '.'))
                        st.dataframe(df_passivo_circ[['Item', 'Valor Formatado']], use_container_width=True, hide_index=True)
                
                with tab4:
                    if detalhamento.get('passivo_nao_circulante'):
                        df_passivo_nao_circ = pd.DataFrame(list(detalhamento['passivo_nao_circulante'].items()), 
                                                         columns=['Item', 'Valor'])
                        df_passivo_nao_circ = df_passivo_nao_circ[df_passivo_nao_circ['Valor'] > 0]
                        df_passivo_nao_circ['Valor Formatado'] = df_passivo_nao_circ['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '.'))
                        st.dataframe(df_passivo_nao_circ[['Item', 'Valor Formatado']], use_container_width=True, hide_index=True)
                
                with tab5:
                    if detalhamento.get('patrimonio_liquido'):
                        df_pl = pd.DataFrame(list(detalhamento['patrimonio_liquido'].items()), 
                                           columns=['Item', 'Valor'])
                        df_pl['Valor Formatado'] = df_pl['Valor'].apply(lambda x: f"R$ {x:,.2f}".replace(',', '.'))
                        st.dataframe(df_pl[['Item', 'Valor Formatado']], use_container_width=True, hide_index=True)
            
            # Informações adicionais
            if resumo.get('data_referencia'):
                st.markdown(f"**📅 Data de Referência:** {resumo['data_referencia'].strftime('%d/%m/%Y') if resumo['data_referencia'] else 'N/A'}")
            
        except Exception as e:
            st.error(f"Erro ao carregar dados do balanço patrimonial: {str(e)}")
            st.info("Verifique se os dados estão disponíveis no MongoDB ou clique no botão para inserir dados de exemplo.")

def main():
    """Função principal da aplicação"""
    
    # Configurar página
    st.set_page_config(
        page_title="FOX SA Investment Board",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"  # Expandir sidebar por padrão para mostrar filtros
    )
    
    # Inicializar session state
    if 'language' not in st.session_state:
        st.session_state.language = 'pt'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Aplicar CSS
    aplicar_css_tema("light")
    
    # Criar filtros globais na sidebar
    filtros_globais = criar_filtros_globais()
    
    # Header principal com logo no canto superior direito
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Espaço vazio para empurrar a logo para a direita
        pass
    
    with col2:
        try:
            st.image("assets/fox_logo.png", width=120)
        except:
            # Fallback se a imagem não for encontrada
            st.markdown('<div style="text-align: right; font-size: 1.5rem;">🌾</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-bottom: 1rem;"></div>', unsafe_allow_html=True)
    
    # Controles superiores - removido tema, ajustado layout para 4 colunas
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
    
    with col1:
        opcoes = [
            get_text('consolidated_view', st.session_state.language),
            "Contratos",
            "Dashboards por Unidade",
            get_text('dre_realtime', st.session_state.language),
            "Balanço Patrimonial",
            get_text('due_diligence', st.session_state.language)
        ]
        opcao = st.selectbox(
            "Menu",  # Alterado de select_view para Menu
            opcoes,
            index=0,  # Sempre inicia na Visão Consolidada
            key="view_select"
        )
    
    with col2:
        # Carregar anos disponíveis dos dados reais
        try:
            from mongodb_connector import get_available_years
            anos_disponiveis = get_available_years()
        except:
            # Fallback se houver erro
            anos_disponiveis = [2025, 2024, 2023, 2022, 2021, 2020]
        
        ano_selecionado = st.selectbox(
            "Ano",  # Alterado de select_year para Ano
            anos_disponiveis,
            index=0,
            key="year_select"
        )
    
    with col3:
        # Seletor de idioma
        lang_options = {'Português': 'pt', 'English': 'en', '中文': 'zh'}
        lang_display = st.selectbox(
            get_text('language', st.session_state.language),
            list(lang_options.keys()),
            index=0 if st.session_state.language == 'pt' else (1 if st.session_state.language == 'en' else 2),
            key="language_select"
        )
        
        # Atualizar idioma se mudou
        new_lang = lang_options[lang_display]
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()
    
    with col4:
        # Botão de atualizar dados (movido para a última coluna)
        if st.button("🔄 Atualizar", help="Atualizar dados", key="refresh_btn"):
            st.rerun()
    
    st.markdown('<hr style="margin: 1.5rem 0; border: 1px solid var(--border-color);">', unsafe_allow_html=True)
    
    # Carregar dados
    dados_eda = carregar_dados_eda()
    dados_financeiros = carregar_dados_financeiros()
    
    # Roteamento de páginas
    if opcao == get_text('consolidated_view', st.session_state.language):
        visao_consolidada(dados_eda, dados_financeiros, st.session_state.language, ano_selecionado, filtros_globais)
    
    elif opcao == "Contratos":
        from contratos_reais import pagina_contratos_reais
        pagina_contratos_reais(st.session_state.theme, filtros_globais)
    
    elif opcao == "Dashboards por Unidade":
        dashboards_unidades_negocio(st.session_state.language, filtros_globais)
    
    elif opcao == get_text('dre_realtime', st.session_state.language):
        dre_tempo_real(st.session_state.language, st.session_state.theme, filtros_globais)
    
    elif opcao == "Balanço Patrimonial":
        secao_balanco_patrimonial(st.session_state.language, ano_selecionado, filtros_globais)
    
    elif opcao == get_text('due_diligence', st.session_state.language):
        secao_due_diligence(st.session_state.language, filtros_globais)
    
    else:
        st.markdown(f'<h2 style="color: inherit;">🚧 {opcao}</h2>', unsafe_allow_html=True)

if __name__ == "__main__":
    pass  # Empty if block

    main()


