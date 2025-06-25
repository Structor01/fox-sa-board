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
# SISTEMA DE IDIOMAS
# ============================================================================

TRANSLATIONS = {
    'pt': {
        # Tela de boas-vindas
        'welcome_title': 'Painel de Resultados em Tempo Real',
        'welcome_subtitle': 'Dashboard executivo para acompanhamento estratégico do agronegócio',
        'dashboard_config': '⚙️ Configurações do Dashboard',
        'period_analysis': '📅 Período de Análise',
        'initial_date': 'Data Inicial:',
        'final_date': 'Data Final:',
        'business_units': '🏢 Unidades de Negócio',
        'fox_graos_desc': 'Fox Grãos (Trade & Logística)',
        'fox_log_desc': 'Fox Log (Transporte & Insumos)',
        'clube_fx_desc': 'Clube FX (Consultoria)',
        'data_status': '🔄 Status dos Dados',
        'last_update': '📊 Última atualização:',
        'update_data': '🔄 Atualizar Dados',
        'access_dashboard': '🚀 Acessar Dashboard Completo',
        
        # Menu principal
        'main_title': '🌾 FOX SA - Painel de Resultados em Tempo Real',
        'select_section': '📊 Selecionar Seção:',
        'period': '📅 Período:',
        'visualization': '👁️ Visualização:',
        'language': '🌐 Idioma:',
        'home': '🏠 Início',
        
        # Seções do menu
        'consolidated_view': 'Visão Consolidada',
        'fox_graos_section': 'Fox Grãos - Trade & Logística',
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
        'fox_graos_title': '🌾 Fox Grãos - Trade Triangular & Logística',
        'triangular_trade': '📈 Operação de Trade Triangular',
        'logistics_section': '🚛 Logística',
        'negotiated_volume': 'Volume Negociado',
        'trade_revenue': 'Receita Trade',
        'trade_margin': 'Margem de Trade',
        'average_cycle': 'Ciclo Médio',
        'last_30_days': 'Últimos 30 dias',
        'vs_previous_month': 'vs mês anterior',
        'vs_average': 'vs média',
        
        # Fox Log
        'fox_log_title': '🚛 Fox Log - Logística & Insumos',
        'transport_revenue': 'Receita Transporte',
        'storage_revenue': 'Receita Armazenagem',
        'transported_volume': 'Volume Transportado',
        'punctuality_sla': 'SLA Pontualidade',
        
        # Clube FX
        'clube_fx_title': '💼 Clube FX - Consultoria',
        'clients_served': 'Clientes Atendidos',
        'consulting_revenue': 'Receita Consultoria',
        'nps_score': 'NPS Score',
        'retention_rate': 'Taxa Retenção',
        'new_clients': 'novos clientes',
        'vs_quarter': 'vs trimestre',
        'ongoing_projects': 'Projetos em Andamento',
        'completed': 'concluído',
        
        # Due Diligence
        'due_diligence_title': '📋 Documentos para Due Diligence e Captação',
        'financial_statements': '📊 Demonstrativos Financeiros',
        'dre_detailed': 'DRE Detalhado por Unidade',
        'balance_sheet': 'Balanço Patrimonial',
        'corporate_structure': '🏢 Estrutura Corporativa',
        'group_organogram': 'Organograma do Grupo',
        'institutional_presentation': '📈 Apresentação Institucional',
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
        'data_status': '🔄 Data Status',
        'last_update': '📊 Last update:',
        'update_data': '🔄 Update Data',
        'access_dashboard': '🚀 Access Complete Dashboard',
        
        # Main menu
        'main_title': '🌾 FOX SA - Real-Time Results Dashboard',
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
        st.info(f"{get_text('last_update', lang)} {ultima_atualizacao}")
        
        if st.button(get_text('update_data', lang), key="refresh_welcome"):
            st.rerun()
    
    # Botão para acessar dashboard
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
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

def secao_due_diligence(lang='pt'):
    """Seção de documentos para due diligence e captação"""
    
    st.markdown(f'<h2 style="color: #FFFFFF; border-bottom: 2px solid #FFD700; padding-bottom: 0.5rem;">{get_text("due_diligence_title", lang)}</h2>', unsafe_allow_html=True)
    
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
            if st.button(f"📄 {get_text('download_pdf', lang)}", key="dre_pdf"):
                st.success("PDF gerado com sucesso!")
        with col_btn2:
            if st.button(f"📊 {get_text('download_excel', lang)}", key="dre_excel"):
                st.success("Excel gerado com sucesso!")
    
    with col2:
        # Balanço Patrimonial
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("balance_sheet", lang)}</h4>', unsafe_allow_html=True)
        
        # Criar Balanço
        balanco_data = criar_balanco_patrimonial(lang)
        st.dataframe(balanco_data, use_container_width=True, height=400)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(f"📄 {get_text('download_pdf', lang)}", key="balanco_pdf"):
                st.success("PDF gerado com sucesso!")
        with col_btn2:
            if st.button(f"📊 {get_text('download_excel', lang)}", key="balanco_excel"):
                st.success("Excel gerado com sucesso!")
    
    # Estrutura Corporativa
    st.markdown(f'<h3 style="color: #FFD700; margin: 2rem 0 1rem 0;">{get_text("corporate_structure", lang)}</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Organograma
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("group_organogram", lang)}</h4>', unsafe_allow_html=True)
        criar_organograma(lang)
        
        if st.button(f"👁️ {get_text('view_document', lang)}", key="organograma_view"):
            st.success("Organograma expandido!")
    
    with col2:
        # Apresentação Institucional
        st.markdown(f'<h4 style="color: #FFFFFF;">{get_text("institutional_presentation", lang)}</h4>', unsafe_allow_html=True)
        criar_deck_institucional(lang)
        
        if st.button(f"📈 {get_text('view_document', lang)}", key="deck_view"):
            st.success("Deck institucional aberto!")

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
# VISÃO CONSOLIDADA (ATUALIZADA COM IDIOMAS)
# ============================================================================

def visao_consolidada(dados_eda, dados_financeiros, lang='pt'):
    """Dashboard geral consolidado"""
    
    st.markdown(f'<h2 style="color: #FFFFFF; border-bottom: 2px solid #C0C0C0; padding-bottom: 0.5rem;">📊 {get_text("consolidated_view", lang)}</h2>', unsafe_allow_html=True)
    
    # KPIs principais com alertas
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = [
        {'label': get_text('gross_revenue', lang), 'value': 'R$ 247M', 'delta': '+12.5%', 'color': '#90EE90'},
        {'label': get_text('ebitda', lang), 'value': 'R$ 89M', 'delta': '+8.3%', 'color': '#FFD700'},
        {'label': get_text('operational_cashflow', lang), 'value': 'R$ 76M', 'delta': '+15.2%', 'color': '#C0C0C0'},
        {'label': get_text('active_clients', lang), 'value': '1,247', 'delta': '+5.8%', 'color': '#87CEEB'}
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
                    ▲ {kpi['delta']} {get_text('vs_previous', lang)}
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Receita x EBITDA (12 meses)
        fig_receita_ebitda = criar_grafico_receita_ebitda(lang)
        st.plotly_chart(fig_receita_ebitda, use_container_width=True)
    
    with col2:
        # Investimento vs Capex
        fig_investimento_capex = criar_grafico_investimento_capex(lang)
        st.plotly_chart(fig_investimento_capex, use_container_width=True)

def criar_grafico_receita_ebitda(lang='pt'):
    """Gráfico de linha Receita x EBITDA"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    receita = [18.5, 19.2, 21.8, 20.1, 22.3, 24.1, 23.8, 25.2, 24.9, 26.1, 25.8, 27.2]
    ebitda = [6.8, 7.1, 8.2, 7.5, 8.9, 9.8, 9.2, 10.1, 9.8, 10.5, 10.2, 11.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses, y=receita,
        mode='lines+markers',
        name=get_text('gross_revenue', lang),
        line=dict(color='#90EE90', width=3),
        marker=dict(size=8),
        hovertemplate=f'<b>%{{x}}</b><br>{get_text("gross_revenue", lang)}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses, y=ebitda,
        mode='lines+markers',
        name=get_text('ebitda', lang),
        line=dict(color='#FFD700', width=3),
        marker=dict(size=8),
        hovertemplate=f'<b>%{{x}}</b><br>{get_text("ebitda", lang)}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=get_text('revenue_ebitda_12m', lang), font=dict(size=18, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=400,
        legend=dict(font=dict(color='#FFFFFF')),
        xaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0'),
        yaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0', title=f'{get_text("value_millions", lang)}')
    )
    
    return fig

def criar_grafico_investimento_capex(lang='pt'):
    """Gráfico de barras empilhadas Investimento vs Capex"""
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    investimento = [2.1, 1.8, 2.5, 2.2, 2.8, 3.1, 2.9, 3.2, 3.0, 3.5, 3.3, 3.8]
    capex = [1.2, 1.5, 1.8, 1.4, 2.1, 2.3, 2.0, 2.4, 2.2, 2.6, 2.5, 2.9]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses, y=investimento,
        name='Investimento' if lang == 'pt' else 'Investment',
        marker=dict(color='#C0C0C0'),
        hovertemplate=f'<b>%{{x}}</b><br>{"Investimento" if lang == "pt" else "Investment"}: R$ %{{y}}M<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=meses, y=capex,
        name='Capex',
        marker=dict(color='#FFD700'),
        hovertemplate='<b>%{x}</b><br>Capex: R$ %{y}M<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=get_text('investment_vs_capex', lang), font=dict(size=18, color='#FFFFFF')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF'),
        height=400,
        barmode='stack',
        legend=dict(font=dict(color='#FFFFFF')),
        xaxis=dict(showgrid=False, color='#C0C0C0'),
        yaxis=dict(showgrid=True, gridcolor='rgba(192, 192, 192, 0.1)', color='#C0C0C0', title=get_text('value_millions', lang))
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
        
        /* Estilizar dataframes */
        .stDataFrame {
            background: #1a1a1a !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
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
    if 'language' not in st.session_state:
        st.session_state.language = 'pt'
    
    # Mostrar tela de boas-vindas ou dashboard principal
    if st.session_state.show_welcome:
        filtros = tela_boas_vindas(st.session_state.language)
    else:
        # Menu de navegação no topo
        st.markdown(f'<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 2rem;">{get_text("main_title", st.session_state.language)}</h1>', unsafe_allow_html=True)
        
        # Controles de navegação
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
        
        with col1:
            opcao = st.selectbox(
                get_text('select_section', st.session_state.language),
                [
                    get_text('consolidated_view', st.session_state.language),
                    get_text('fox_graos_section', st.session_state.language), 
                    get_text('fox_log_section', st.session_state.language),
                    get_text('clube_fx_section', st.session_state.language),
                    get_text('financial_performance', st.session_state.language),
                    get_text('dre_realtime', st.session_state.language),
                    get_text('insights_trends', st.session_state.language),
                    get_text('projections_scenarios', st.session_state.language),
                    get_text('roadmap_actions', st.session_state.language),
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
        
        with col4:
            # Seletor de idioma
            lang_options = {'Português': 'pt', 'English': 'en'}
            lang_display = st.selectbox(
                get_text('language', st.session_state.language),
                list(lang_options.keys()),
                index=0 if st.session_state.language == 'pt' else 1,
                key="language_select"
            )
            
            # Atualizar idioma se mudou
            new_lang = lang_options[lang_display]
            if new_lang != st.session_state.language:
                st.session_state.language = new_lang
                st.rerun()
        
        with col5:
            if st.button(get_text('home', st.session_state.language), key="home_btn"):
                st.session_state.show_welcome = True
                st.rerun()
        
        st.markdown('<hr style="margin: 1.5rem 0; border: 1px solid #333333;">', unsafe_allow_html=True)
        
        # Carregar dados
        dados_eda = carregar_dados_eda()
        dados_financeiros = carregar_dados_financeiros()
        
        # Roteamento de páginas
        if opcao == get_text('consolidated_view', st.session_state.language):
            visao_consolidada(dados_eda, dados_financeiros, st.session_state.language)
        
        elif opcao == get_text('due_diligence', st.session_state.language):
            secao_due_diligence(st.session_state.language)
        
        else:
            st.markdown(f'<h2 style="color: #FFFFFF;">🚧 {opcao}</h2>', unsafe_allow_html=True)
            st.info(get_text('in_development', st.session_state.language))

if __name__ == "__main__":
    main()

