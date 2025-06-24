import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Importar sistema de autenticação
from auth import (
    check_authentication, 
    show_login_page, 
    show_user_info, 
    get_current_user,
    check_permission
)

# Importar dados estruturados para EDA
from gerar_dados_fox import (
    gerar_dados_fox_graos, 
    gerar_dados_fox_log, 
    gerar_dados_clube_fx,
    gerar_dados_consolidados,
    obter_dados_para_eda
)

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

def configurar_pagina():
    """Configuração inicial da página seguindo melhores práticas"""
    st.set_page_config(
        page_title="FOX SA Investment Board",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ============================================================================
# CARREGAMENTO E CACHE DE DADOS
# ============================================================================

@st.cache_data
def carregar_dados_eda():
    """Carrega dados estruturados para EDA com cache"""
    return obter_dados_para_eda()

@st.cache_data
def carregar_dados_financeiros():
    """Carrega dados financeiros com cache"""
    bal_graos, dre_graos, comm_graos = gerar_dados_fox_graos()
    bal_log, dre_log, op_log = gerar_dados_fox_log()
    bal_fx, dre_fx, op_fx = gerar_dados_clube_fx()
    bal_consolidado, dre_consolidado = gerar_dados_consolidados()
    
    return {
        'fox_graos': {'balanco': bal_graos, 'dre': dre_graos, 'commodities': comm_graos},
        'fox_log': {'balanco': bal_log, 'dre': dre_log, 'operacional': op_log},
        'clube_fx': {'balanco': bal_fx, 'dre': dre_fx, 'operacional': op_fx},
        'consolidado': {'balanco': bal_consolidado, 'dre': dre_consolidado}
    }

# ============================================================================
# PALETA DE CORES PROFISSIONAL (PRETO E PRATA)
# ============================================================================

CORES_PROFISSIONAIS = {
    'primary': '#C0C0C0',      # Prata
    'secondary': '#808080',     # Cinza médio
    'accent': '#A0A0A0',       # Prata escuro
    'background': '#000000',    # Preto
    'surface': '#1A1A1A',      # Preto suave
    'text_primary': '#FFFFFF',  # Branco
    'text_secondary': '#C0C0C0', # Prata
    'border': '#333333',       # Cinza escuro
    'success': '#90EE90',      # Verde suave
    'warning': '#FFD700',      # Dourado
    'error': '#FF6B6B'         # Vermelho suave
}

# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO OTIMIZADAS
# ============================================================================

def criar_grafico_receita_temporal_premium(dados_temporais, ano_selecionado):
    """Gráfico de receita temporal com design premium"""
    df_filtrado = dados_temporais[dados_temporais['ano'] == ano_selecionado]
    
    fig = px.line(
        df_filtrado,
        x='mes_num',
        y='receita',
        color='empresa',
        title=f"Monthly Revenue Evolution - {ano_selecionado}",
        labels={'receita': 'Revenue (R$ thousands)', 'mes_num': 'Month'},
        color_discrete_sequence=[CORES_PROFISSIONAIS['primary'], 
                               CORES_PROFISSIONAIS['secondary'], 
                               CORES_PROFISSIONAIS['accent']]
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='white'))
    )
    
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CORES_PROFISSIONAIS['text_primary'], family='Inter', size=12),
        title=dict(
            font=dict(size=20, color=CORES_PROFISSIONAIS['text_primary'], weight='bold'), 
            x=0.02, 
            y=0.95
        ),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(192, 192, 192, 0.1)', 
            showline=True,
            linecolor=CORES_PROFISSIONAIS['border'],
            color=CORES_PROFISSIONAIS['text_secondary'],
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(192, 192, 192, 0.1)', 
            showline=True,
            linecolor=CORES_PROFISSIONAIS['border'],
            color=CORES_PROFISSIONAIS['text_secondary'],
            tickfont=dict(size=11)
        ),
        legend=dict(
            font=dict(color=CORES_PROFISSIONAIS['text_primary'], size=12),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor=CORES_PROFISSIONAIS['border'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def criar_heatmap_performance_premium(performance_data):
    """Heatmap de performance com design premium"""
    df_pivot = performance_data.pivot_table(
        index='empresa', 
        columns='mes', 
        values='performance', 
        aggfunc='mean'
    )
    
    meses_ordem = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    df_pivot = df_pivot.reindex(columns=meses_ordem)
    
    # Colorscale personalizada em tons de prata
    colorscale = [
        [0.0, '#000000'],
        [0.25, '#333333'],
        [0.5, '#666666'],
        [0.75, '#999999'],
        [1.0, '#C0C0C0']
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        colorscale=colorscale,
        showscale=True,
        text=np.round(df_pivot.values, 1),
        texttemplate="%{text}%",
        textfont=dict(color='white', size=11, family='Inter')
    ))
    
    fig.update_layout(
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text="Monthly Performance Heatmap",
            font=dict(size=20, color='#FFFFFF', weight='bold'), 
            x=0.02, 
            y=0.95
        ),
        xaxis=dict(
            color='#C0C0C0',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            color='#C0C0C0',
            tickfont=dict(size=11)
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def criar_grafico_commodities_premium(commodities_data, ano_selecionado):
    """Gráfico de commodities com design premium"""
    df_filtrado = commodities_data[commodities_data['ano'] == ano_selecionado]
    df_agrupado = df_filtrado.groupby('commodity')['volume_comercializado'].sum().reset_index()
    
    fig = go.Figure(data=[go.Pie(
        labels=df_agrupado['commodity'],
        values=df_agrupado['volume_comercializado'],
        hole=0.4,
        marker=dict(
            colors=['#C0C0C0', '#808080', '#A0A0A0'],
            line=dict(color='#000000', width=2)
        ),
        textfont=dict(color='white', size=12, family='Inter'),
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text=f"Commodity Volume Distribution - {ano_selecionado}",
            font=dict(size=20, color='#FFFFFF', weight='bold'), 
            x=0.02, 
            y=0.95
        ),
        showlegend=True,
        legend=dict(
            font=dict(color='#FFFFFF', size=12)
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def criar_grafico_receita_barras_premium(dados_temporais, ano_selecionado):
    """Gráfico de barras premium"""
    df_filtrado = dados_temporais[dados_temporais['ano'] == ano_selecionado]
    df_agrupado = df_filtrado.groupby('empresa')['receita'].sum().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_agrupado['empresa'],
            y=df_agrupado['receita'],
            marker=dict(
                color=['#C0C0C0', '#808080', '#A0A0A0'],
                line=dict(color='#000000', width=1)
            ),
            text=df_agrupado['receita'].apply(lambda x: f'R$ {x:,.0f}k'),
            textposition='outside',
            textfont=dict(color='#FFFFFF', size=11, family='Inter')
        )
    ])
    
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text=f"Total Revenue by Company - {ano_selecionado}",
            font=dict(size=20, color='#FFFFFF', weight='bold'), 
            x=0.02, 
            y=0.95
        ),
        xaxis=dict(
            showgrid=False, 
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(192, 192, 192, 0.1)', 
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11)
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def criar_mapa_goias_premium(dados_mapa):
    """Mapa de Goiás com produtores e compradores"""
    import plotly.graph_objects as go
    
    # Separar dados por tipo
    produtores = dados_mapa[dados_mapa['tipo'] == 'produtor']
    compradores = dados_mapa[dados_mapa['tipo'] == 'comprador']
    hubs = dados_mapa[dados_mapa['tipo'] == 'hub']
    
    fig = go.Figure()
    
    # Adicionar produtores
    fig.add_trace(go.Scattermapbox(
        lat=produtores['latitude'],
        lon=produtores['longitude'],
        mode='markers',
        marker=dict(
            size=produtores['volume_anual'] / 1000,  # Tamanho baseado no volume
            color='#90EE90',  # Verde para produtores
            symbol='triangle-up',
            sizemode='diameter',
            sizemin=8,
            sizemax=25,
            opacity=0.8
        ),
        text=produtores.apply(lambda x: f"<b>{x['cidade']}</b><br>" +
                                      f"Tipo: Produtor<br>" +
                                      f"Volume: {x['volume_anual']:,.0f} ton/ano<br>" +
                                      f"LTV: R$ {x['ltv']:,.0f}<br>" +
                                      f"Empresa: {x['empresa_responsavel']}<br>" +
                                      f"Commodities: {', '.join(x['commodities_principais'])}", axis=1),
        hovertemplate='%{text}<extra></extra>',
        name='Produtores',
        showlegend=True
    ))
    
    # Adicionar compradores
    fig.add_trace(go.Scattermapbox(
        lat=compradores['latitude'],
        lon=compradores['longitude'],
        mode='markers',
        marker=dict(
            size=compradores['volume_anual'] / 1000,
            color='#FFD700',  # Dourado para compradores
            symbol='circle',
            sizemode='diameter',
            sizemin=8,
            sizemax=25,
            opacity=0.8
        ),
        text=compradores.apply(lambda x: f"<b>{x['cidade']}</b><br>" +
                                        f"Tipo: Comprador<br>" +
                                        f"Volume: {x['volume_anual']:,.0f} ton/ano<br>" +
                                        f"LTV: R$ {x['ltv']:,.0f}<br>" +
                                        f"Empresa: {x['empresa_responsavel']}<br>" +
                                        f"Commodities: {', '.join(x['commodities_principais'])}", axis=1),
        hovertemplate='%{text}<extra></extra>',
        name='Compradores',
        showlegend=True
    ))
    
    # Adicionar hubs
    if not hubs.empty:
        fig.add_trace(go.Scattermapbox(
            lat=hubs['latitude'],
            lon=hubs['longitude'],
            mode='markers',
            marker=dict(
                size=hubs['volume_anual'] / 2000,
                color='#C0C0C0',  # Prata para hubs
                symbol='diamond',
                sizemode='diameter',
                sizemin=15,
                sizemax=35,
                opacity=0.9
            ),
            text=hubs.apply(lambda x: f"<b>{x['cidade']}</b><br>" +
                                     f"Tipo: Hub Central<br>" +
                                     f"Volume: {x['volume_anual']:,.0f} ton/ano<br>" +
                                     f"LTV: R$ {x['ltv']:,.0f}<br>" +
                                     f"Empresa: {x['empresa_responsavel']}<br>" +
                                     f"Commodities: {', '.join(x['commodities_principais'])}", axis=1),
            hovertemplate='%{text}<extra></extra>',
            name='Hub Central',
            showlegend=True
        ))
    
    # Configurar layout do mapa
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",  # Tema escuro
            center=dict(lat=-16.8, lon=-49.5),  # Centro de Goiás
            zoom=6.5
        ),
        height=500,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text="Mapa de Produtores e Compradores - Goiás",
            font=dict(size=20, color='#FFFFFF', weight='bold'),
            x=0.02,
            y=0.95
        ),
        legend=dict(
            font=dict(color='#FFFFFF', size=12),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='#333333',
            borderwidth=1,
            x=0.02,
            y=0.02
        )
    )
    
    return fig

def criar_grafico_ltv_segmentos(dados_ltv):
    """Gráfico de LTV por segmentos"""
    import plotly.graph_objects as go
    
    # Agrupar por segmento
    ltv_por_segmento = dados_ltv.groupby('segmento').agg({
        'ltv_total': ['count', 'mean', 'sum'],
        'tempo_relacionamento': 'mean'
    }).round(0)
    
    # Flatten column names
    ltv_por_segmento.columns = ['_'.join(col).strip() for col in ltv_por_segmento.columns]
    ltv_por_segmento = ltv_por_segmento.reset_index()
    
    # Cores por segmento
    cores_segmento = {
        'Premium': '#FFD700',
        'Gold': '#C0C0C0', 
        'Silver': '#CD7F32',
        'Bronze': '#8B4513'
    }
    
    fig = go.Figure()
    
    # Gráfico de barras para LTV total por segmento
    fig.add_trace(go.Bar(
        x=ltv_por_segmento['segmento'],
        y=ltv_por_segmento['ltv_total_sum'],
        marker=dict(
            color=[cores_segmento.get(seg, '#666666') for seg in ltv_por_segmento['segmento']],
            line=dict(color='#000000', width=1)
        ),
        text=ltv_por_segmento['ltv_total_sum'].apply(lambda x: f'R$ {x/1000000:.1f}M'),
        textposition='outside',
        textfont=dict(color='#FFFFFF', size=11, family='Inter'),
        name='LTV Total por Segmento'
    ))
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text="LTV Total por Segmento de Cliente",
            font=dict(size=18, color='#FFFFFF', weight='bold'),
            x=0.02,
            y=0.95
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            title=dict(text="Segmento", font=dict(color='#C0C0C0'))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(192, 192, 192, 0.1)',
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            title=dict(text="LTV Total (R$)", font=dict(color='#C0C0C0'))
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def criar_scatter_ltv_tempo(dados_ltv):
    """Scatter plot LTV vs Tempo de Relacionamento"""
    import plotly.graph_objects as go
    
    # Cores por segmento
    cores_segmento = {
        'Premium': '#FFD700',
        'Gold': '#C0C0C0', 
        'Silver': '#CD7F32',
        'Bronze': '#8B4513'
    }
    
    fig = go.Figure()
    
    # Adicionar pontos por segmento
    for segmento in dados_ltv['segmento'].unique():
        dados_seg = dados_ltv[dados_ltv['segmento'] == segmento]
        
        fig.add_trace(go.Scatter(
            x=dados_seg['tempo_relacionamento'],
            y=dados_seg['ltv_total'],
            mode='markers',
            marker=dict(
                color=cores_segmento.get(segmento, '#666666'),
                size=dados_seg['receita_anual'] / 200000,  # Tamanho baseado na receita
                sizemode='diameter',
                sizemin=8,
                sizemax=25,
                opacity=0.8,
                line=dict(color='#000000', width=1)
            ),
            text=dados_seg.apply(lambda x: f"<b>{x['cliente']}</b><br>" +
                                          f"Segmento: {x['segmento']}<br>" +
                                          f"LTV: R$ {x['ltv_total']:,.0f}<br>" +
                                          f"Tempo: {x['tempo_relacionamento']:.1f} anos<br>" +
                                          f"Receita Anual: R$ {x['receita_anual']:,.0f}<br>" +
                                          f"Empresa FOX: {x['empresa_fox']}", axis=1),
            hovertemplate='%{text}<extra></extra>',
            name=segmento
        ))
    
    fig.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text="LTV vs Tempo de Relacionamento",
            font=dict(size=18, color='#FFFFFF', weight='bold'),
            x=0.02,
            y=0.95
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(192, 192, 192, 0.1)',
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            title=dict(text="Tempo de Relacionamento (anos)", font=dict(color='#C0C0C0'))
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(192, 192, 192, 0.1)',
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            title=dict(text="LTV Total (R$)", font=dict(color='#C0C0C0'))
        ),
        legend=dict(
            font=dict(color='#FFFFFF', size=12),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='#333333',
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# ============================================================================
# COMPONENTES DE INTERFACE PREMIUM
# ============================================================================

def exibir_metricas_principais_premium(dados_financeiros):
    """Métricas principais com design premium"""
    dre_consolidado = dados_financeiros['consolidado']['dre']
    
    col1, col2, col3, col4 = st.columns(4)
    
    metricas = [
        {
            'label': 'Net Revenue',
            'value': f"R$ {dre_consolidado['Receita Operacional Líquida']:,.0f}k",
            'delta': '+12.5%',
            'color': CORES_PROFISSIONAIS['success']
        },
        {
            'label': 'EBITDA',
            'value': f"R$ {dre_consolidado['EBITDA']:,.0f}k",
            'delta': '+8.2%',
            'color': CORES_PROFISSIONAIS['success']
        },
        {
            'label': 'Net Profit',
            'value': f"R$ {dre_consolidado['Lucro Líquido']:,.0f}k",
            'delta': '-15.3%',
            'color': CORES_PROFISSIONAIS['error']
        },
        {
            'label': 'EBITDA Margin',
            'value': f"{(dre_consolidado['EBITDA'] / dre_consolidado['Receita Operacional Líquida']) * 100:.1f}%",
            'delta': '+0.5pp',
            'color': CORES_PROFISSIONAIS['success']
        }
    ]
    
    colunas = [col1, col2, col3, col4]
    
    for i, metrica in enumerate(metricas):
        with colunas[i]:
            st.markdown(f'''
            <div class="metric-card-premium">
                <div class="metric-label">{metrica['label']}</div>
                <div class="metric-value">{metrica['value']}</div>
                <div class="metric-delta" style="color: {metrica['color']}">{metrica['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)

def criar_sidebar_controles_premium():
    """Sidebar com controles premium"""
    st.sidebar.markdown('<div class="sidebar-header">Dashboard Controls</div>', unsafe_allow_html=True)
    
    # Seletor de ano
    anos_disponiveis = list(range(2019, 2025))
    ano_selecionado = st.sidebar.selectbox(
        "Select Year",
        anos_disponiveis,
        index=len(anos_disponiveis)-1
    )
    
    # Seletor de visualização
    tipos_visualizacao = ["Standard", "Detailed", "Executive"]
    tipo_selecionado = st.sidebar.selectbox(
        "View Type",
        tipos_visualizacao,
        index=0
    )
    
    return ano_selecionado, tipo_selecionado

def exibir_tabela_premium(migracao_data):
    """Tabela com design premium"""
    st.markdown('<div class="section-header-premium">Top States by Volume</div>', unsafe_allow_html=True)
    
    df_agrupado = migracao_data.groupby('estado').agg({
        'volume_entrada': 'sum',
        'volume_saida': 'sum',
        'saldo_liquido': 'sum'
    }).reset_index()
    
    df_agrupado = df_agrupado.sort_values('volume_entrada', ascending=False).head(8)
    
    # Formatar dados
    df_agrupado['volume_entrada'] = df_agrupado['volume_entrada'].apply(lambda x: f"{x:,.0f}")
    df_agrupado['volume_saida'] = df_agrupado['volume_saida'].apply(lambda x: f"{x:,.0f}")
    df_agrupado['saldo_liquido'] = df_agrupado['saldo_liquido'].apply(lambda x: f"{x:,.0f}")
    
    df_agrupado.columns = ['State', 'Inbound Volume', 'Outbound Volume', 'Net Balance']
    
    st.dataframe(
        df_agrupado, 
        use_container_width=True, 
        hide_index=True,
        height=300
    )

# ============================================================================
# PÁGINAS DO DASHBOARD
# ============================================================================

def pagina_visao_consolidada_premium(dados_eda, dados_financeiros, ano_selecionado):
    """Página principal premium"""
    st.markdown('<div class="page-header">Consolidated Overview</div>', unsafe_allow_html=True)
    
    # Métricas principais
    exibir_metricas_principais_premium(dados_financeiros)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        fig_receita = criar_grafico_receita_barras_premium(dados_eda['dados_temporais'], ano_selecionado)
        st.plotly_chart(fig_receita, use_container_width=True)
    
    with col2:
        fig_commodities = criar_grafico_commodities_premium(dados_eda['commodities_temporais'], ano_selecionado)
        st.plotly_chart(fig_commodities, use_container_width=True)
    
    # Gráfico de evolução temporal
    st.markdown('<div class="section-header-premium">Revenue Evolution</div>', unsafe_allow_html=True)
    fig_temporal = criar_grafico_receita_temporal_premium(dados_eda['dados_temporais'], ano_selecionado)
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Heatmap de performance
    st.markdown('<div class="section-header-premium">Performance Heatmap</div>', unsafe_allow_html=True)
    fig_heatmap = criar_heatmap_performance_premium(dados_eda['performance_mensal'])
    st.plotly_chart(fig_heatmap, use_container_width=True)

def pagina_analise_commodities_premium(dados_eda, ano_selecionado):
    """Página de análise por commodities premium"""
    st.markdown('<div class="page-header">Commodity Analysis</div>', unsafe_allow_html=True)
    
    df_commodities = dados_eda['commodities_temporais']
    df_filtrado = df_commodities[df_commodities['ano'] == ano_selecionado]
    
    # Métricas por commodity
    col1, col2, col3 = st.columns(3)
    
    commodities = ['Soja', 'Milho', 'Sorgo']
    cores_commodities = [CORES_PROFISSIONAIS['primary'], 
                        CORES_PROFISSIONAIS['secondary'], 
                        CORES_PROFISSIONAIS['accent']]
    
    for i, commodity in enumerate(commodities):
        df_commodity = df_filtrado[df_filtrado['commodity'] == commodity]
        volume_total = df_commodity['volume_comercializado'].sum()
        preco_medio = df_commodity['preco_medio'].mean()
        
        with [col1, col2, col3][i]:
            st.markdown(f'''
            <div class="metric-card-premium">
                <div class="metric-label">{commodity} Volume</div>
                <div class="metric-value">{volume_total:,.0f} tons</div>
                <div class="metric-delta" style="color: {cores_commodities[i]}">Avg: R$ {preco_medio:,.0f}/ton</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Gráfico de evolução de preços
    st.markdown('<div class="section-header-premium">Price Evolution</div>', unsafe_allow_html=True)
    
    fig_precos = px.line(
        df_filtrado,
        x='mes_num',
        y='preco_medio',
        color='commodity',
        title=f"Commodity Price Evolution - {ano_selecionado}",
        labels={'preco_medio': 'Average Price (R$/ton)', 'mes_num': 'Month'},
        color_discrete_sequence=cores_commodities
    )
    
    fig_precos.update_traces(line=dict(width=3), marker=dict(size=8))
    
    fig_precos.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=CORES_PROFISSIONAIS['text_primary'], family='Inter'),
        title=dict(
            font=dict(size=20, color=CORES_PROFISSIONAIS['text_primary'], weight='bold'), 
            x=0.02, 
            y=0.95
        ),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(192, 192, 192, 0.1)', 
            showline=True,
            linecolor=CORES_PROFISSIONAIS['border'],
            color=CORES_PROFISSIONAIS['text_secondary']
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(192, 192, 192, 0.1)', 
            showline=True,
            linecolor=CORES_PROFISSIONAIS['border'],
            color=CORES_PROFISSIONAIS['text_secondary']
        ),
        legend=dict(
            font=dict(color=CORES_PROFISSIONAIS['text_primary']),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor=CORES_PROFISSIONAIS['border'],
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig_precos, use_container_width=True)
    
    # Tabela premium
    exibir_tabela_premium(dados_eda['migracao_commodities'])

def pagina_mapa_goias_premium(dados_eda):
    """Página do mapa de Goiás com produtores e compradores"""
    st.markdown('<div class="page-header">Geographic Map - Goiás</div>', unsafe_allow_html=True)
    
    # Métricas do mapa
    dados_mapa = dados_eda['mapa_goias']
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_pontos = len(dados_mapa)
    total_produtores = len(dados_mapa[dados_mapa['tipo'] == 'produtor'])
    total_compradores = len(dados_mapa[dados_mapa['tipo'] == 'comprador'])
    volume_total = dados_mapa['volume_anual'].sum()
    
    metricas_mapa = [
        {'label': 'Total Points', 'value': f'{total_pontos}', 'delta': 'Active locations', 'color': '#C0C0C0'},
        {'label': 'Producers', 'value': f'{total_produtores}', 'delta': 'Supply points', 'color': '#90EE90'},
        {'label': 'Buyers', 'value': f'{total_compradores}', 'delta': 'Demand points', 'color': '#FFD700'},
        {'label': 'Total Volume', 'value': f'{volume_total:,.0f}', 'delta': 'tons/year', 'color': '#C0C0C0'}
    ]
    
    for i, metrica in enumerate(metricas_mapa):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div class="metric-card-premium">
                <div class="metric-label">{metrica['label']}</div>
                <div class="metric-value">{metrica['value']}</div>
                <div class="metric-delta" style="color: {metrica['color']}">{metrica['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mapa principal
    fig_mapa = criar_mapa_goias_premium(dados_mapa)
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    # Análise por tipo
    st.markdown('<div class="section-header-premium">Analysis by Type</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volume por tipo
        volume_por_tipo = dados_mapa.groupby('tipo')['volume_anual'].sum().reset_index()
        
        fig_volume_tipo = go.Figure(data=[go.Bar(
            x=volume_por_tipo['tipo'],
            y=volume_por_tipo['volume_anual'],
            marker=dict(
                color=['#90EE90', '#FFD700', '#C0C0C0'],
                line=dict(color='#000000', width=1)
            ),
            text=volume_por_tipo['volume_anual'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            textfont=dict(color='#FFFFFF', size=11, family='Inter')
        )])
        
        fig_volume_tipo.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF', family='Inter'),
            title=dict(
                text="Volume by Type",
                font=dict(size=18, color='#FFFFFF', weight='bold'),
                x=0.02,
                y=0.95
            ),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#333333',
                color='#C0C0C0',
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(192, 192, 192, 0.1)',
                showline=True,
                linecolor='#333333',
                color='#C0C0C0',
                tickfont=dict(size=11)
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig_volume_tipo, use_container_width=True)
    
    with col2:
        # LTV por tipo
        ltv_por_tipo = dados_mapa.groupby('tipo')['ltv'].sum().reset_index()
        
        fig_ltv_tipo = go.Figure(data=[go.Pie(
            labels=ltv_por_tipo['tipo'],
            values=ltv_por_tipo['ltv'],
            hole=0.4,
            marker=dict(
                colors=['#90EE90', '#FFD700', '#C0C0C0'],
                line=dict(color='#000000', width=2)
            ),
            textfont=dict(color='white', size=12, family='Inter'),
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig_ltv_tipo.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF', family='Inter'),
            title=dict(
                text="LTV Distribution by Type",
                font=dict(size=18, color='#FFFFFF', weight='bold'),
                x=0.02,
                y=0.95
            ),
            showlegend=True,
            legend=dict(
                font=dict(color='#FFFFFF', size=12)
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig_ltv_tipo, use_container_width=True)
    
    # Tabela detalhada
    st.markdown('<div class="section-header-premium">Detailed Location Data</div>', unsafe_allow_html=True)
    
    # Preparar dados para tabela
    df_tabela = dados_mapa[['cidade', 'tipo', 'volume_anual', 'ltv', 'empresa_responsavel']].copy()
    df_tabela['volume_anual'] = df_tabela['volume_anual'].apply(lambda x: f"{x:,.0f}")
    df_tabela['ltv'] = df_tabela['ltv'].apply(lambda x: f"R$ {x:,.0f}")
    df_tabela.columns = ['City', 'Type', 'Annual Volume (tons)', 'LTV', 'FOX Company']
    
    st.dataframe(
        df_tabela,
        use_container_width=True,
        hide_index=True,
        height=400
    )

def pagina_analise_ltv_premium(dados_eda):
    """Página de análise de LTV"""
    st.markdown('<div class="page-header">LTV Analysis</div>', unsafe_allow_html=True)
    
    dados_ltv = dados_eda['ltv_detalhado']
    
    # Métricas principais de LTV
    col1, col2, col3, col4 = st.columns(4)
    
    ltv_total = dados_ltv['ltv_total'].sum()
    ltv_medio = dados_ltv['ltv_total'].mean()
    tempo_medio = dados_ltv['tempo_relacionamento'].mean()
    clientes_ativos = len(dados_ltv[dados_ltv['status'] == 'Ativo'])
    
    metricas_ltv = [
        {'label': 'Total LTV', 'value': f'R$ {ltv_total/1000000:.1f}M', 'delta': 'All customers', 'color': '#FFD700'},
        {'label': 'Average LTV', 'value': f'R$ {ltv_medio/1000000:.1f}M', 'delta': 'Per customer', 'color': '#C0C0C0'},
        {'label': 'Avg Relationship', 'value': f'{tempo_medio:.1f} years', 'delta': 'Customer tenure', 'color': '#90EE90'},
        {'label': 'Active Customers', 'value': f'{clientes_ativos}', 'delta': f'{len(dados_ltv)} total', 'color': '#C0C0C0'}
    ]
    
    for i, metrica in enumerate(metricas_ltv):
        with [col1, col2, col3, col4][i]:
            st.markdown(f'''
            <div class="metric-card-premium">
                <div class="metric-label">{metrica['label']}</div>
                <div class="metric-value">{metrica['value']}</div>
                <div class="metric-delta" style="color: {metrica['color']}">{metrica['delta']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos de LTV
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ltv_segmentos = criar_grafico_ltv_segmentos(dados_ltv)
        st.plotly_chart(fig_ltv_segmentos, use_container_width=True)
    
    with col2:
        fig_scatter_ltv = criar_scatter_ltv_tempo(dados_ltv)
        st.plotly_chart(fig_scatter_ltv, use_container_width=True)
    
    # Análise por empresa FOX
    st.markdown('<div class="section-header-premium">LTV by FOX Company</div>', unsafe_allow_html=True)
    
    ltv_por_empresa = dados_ltv.groupby('empresa_fox').agg({
        'ltv_total': ['count', 'mean', 'sum'],
        'tempo_relacionamento': 'mean'
    }).round(0)
    
    # Flatten column names
    ltv_por_empresa.columns = ['_'.join(col).strip() for col in ltv_por_empresa.columns]
    ltv_por_empresa = ltv_por_empresa.reset_index()
    
    fig_ltv_empresa = go.Figure()
    
    # Gráfico de barras agrupadas
    fig_ltv_empresa.add_trace(go.Bar(
        name='Number of Customers',
        x=ltv_por_empresa['empresa_fox'],
        y=ltv_por_empresa['ltv_total_count'],
        yaxis='y',
        marker=dict(color='#C0C0C0', line=dict(color='#000000', width=1)),
        text=ltv_por_empresa['ltv_total_count'],
        textposition='outside'
    ))
    
    fig_ltv_empresa.add_trace(go.Bar(
        name='Average LTV (R$ M)',
        x=ltv_por_empresa['empresa_fox'],
        y=ltv_por_empresa['ltv_total_mean'] / 1000000,
        yaxis='y2',
        marker=dict(color='#FFD700', line=dict(color='#000000', width=1)),
        text=ltv_por_empresa['ltv_total_mean'].apply(lambda x: f'R$ {x/1000000:.1f}M'),
        textposition='outside'
    ))
    
    fig_ltv_empresa.update_layout(
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Inter'),
        title=dict(
            text="LTV Analysis by FOX Company",
            font=dict(size=18, color='#FFFFFF', weight='bold'),
            x=0.02,
            y=0.95
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            title='Number of Customers',
            showgrid=True,
            gridcolor='rgba(192, 192, 192, 0.1)',
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            side='left'
        ),
        yaxis2=dict(
            title='Average LTV (R$ M)',
            showgrid=False,
            showline=True,
            linecolor='#333333',
            color='#C0C0C0',
            tickfont=dict(size=11),
            side='right',
            overlaying='y'
        ),
        legend=dict(
            font=dict(color='#FFFFFF', size=12),
            bgcolor='rgba(26, 26, 26, 0.8)',
            bordercolor='#333333',
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig_ltv_empresa, use_container_width=True)
    
    # Tabela de clientes top
    st.markdown('<div class="section-header-premium">Top Customers by LTV</div>', unsafe_allow_html=True)
    
    top_clientes = dados_ltv.nlargest(10, 'ltv_total')[['cliente', 'segmento', 'ltv_total', 'tempo_relacionamento', 'empresa_fox', 'cidade']].copy()
    top_clientes['ltv_total'] = top_clientes['ltv_total'].apply(lambda x: f"R$ {x:,.0f}")
    top_clientes['tempo_relacionamento'] = top_clientes['tempo_relacionamento'].apply(lambda x: f"{x:.1f} years")
    top_clientes.columns = ['Customer', 'Segment', 'LTV', 'Relationship Time', 'FOX Company', 'City']
    
    st.dataframe(
        top_clientes,
        use_container_width=True,
        hide_index=True,
        height=400
    )

# ============================================================================
# CSS PREMIUM (PRETO E PRATA)
# ============================================================================

def aplicar_css_premium():
    """CSS premium com design minimalista preto e prata"""
    
    # Definir cores localmente para interpolação
    cores = {
        'primary': '#C0C0C0',      # Prata
        'secondary': '#808080',     # Cinza médio
        'accent': '#A0A0A0',       # Prata escuro
        'background': '#000000',    # Preto
        'surface': '#1A1A1A',      # Preto suave
        'text_primary': '#FFFFFF',  # Branco
        'text_secondary': '#C0C0C0', # Prata
        'border': '#333333',       # Cinza escuro
        'success': '#90EE90',      # Verde suave
        'warning': '#FFD700',      # Dourado
        'error': '#FF6B6B'         # Vermelho suave
    }
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {{
            background: linear-gradient(135deg, {cores['background']} 0%, {cores['surface']} 100%);
            color: {cores['text_primary']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}
        
        .page-header {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {cores['text_primary']};
            margin: 0 0 2rem 0;
            text-align: left;
            letter-spacing: -1px;
            border-bottom: 3px solid {cores['primary']};
            padding-bottom: 1rem;
        }}
        
        .section-header-premium {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {cores['text_primary']};
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid {cores['border']};
        }}
        
        .sidebar-header {{
            font-size: 1.2rem;
            font-weight: 600;
            color: {cores['text_primary']};
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid {cores['border']};
        }}
        
        .metric-card-premium {{
            background: linear-gradient(135deg, {cores['surface']} 0%, #2A2A2A 100%);
            border: 1px solid {cores['border']};
            border-radius: 12px;
            padding: 2rem 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card-premium:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
            border-color: {cores['primary']};
        }}
        
        .metric-card-premium::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, {cores['primary']}, {cores['secondary']});
        }}
        
        .metric-label {{
            color: {cores['text_secondary']};
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.75rem;
        }}
        
        .metric-value {{
            color: {cores['text_primary']};
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }}
        
        .metric-delta {{
            font-size: 0.875rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        .css-1d391kg {{
            background: linear-gradient(180deg, {cores['surface']} 0%, {cores['background']} 100%);
            border-right: 1px solid {cores['border']};
        }}
        
        .css-1d391kg .stSelectbox label {{
            color: {cores['text_primary']} !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            margin-bottom: 0.5rem !important;
        }}
        
         .css-1d391kg .stSelectbox > div > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        /* Inputs e selectboxes pretos */
        .stSelectbox > div > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stSelectbox > div > div > div {{
            background: {cores['background']} !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stSelectbox > div > div:hover {{
            border-color: {cores['primary']} !important;
        }}
        
        /* Dropdown options */
        .stSelectbox > div > div > div > div {{
            background: {cores['background']} !important;
            color: {cores['text_primary']} !important;
        }}
        
        /* Text inputs */
        .stTextInput > div > div > input {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {cores['primary']} !important;
            box-shadow: 0 0 0 1px {cores['primary']} !important;
        }}
        
        /* Number inputs */
        .stNumberInput > div > div > input {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stNumberInput > div > div > input:focus {{
            border-color: {cores['primary']} !important;
            box-shadow: 0 0 0 1px {cores['primary']} !important;
        }}
        
        /* Botões pretos */
        .stButton > button {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background: {cores['surface']} !important;
            border-color: {cores['primary']} !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(0) !important;
        }}
        
        /* Botão de login específico */
        .stForm button {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
            font-weight: 500 !important;
            width: 100% !important;
            padding: 0.75rem !important;
            transition: all 0.3s ease !important;
        }}
        
        .stForm button:hover {{
            background: {cores['surface']} !important;
            border-color: {cores['primary']} !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }}
        
        /* Checkboxes e radio buttons */
        .stCheckbox > label > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
        }}
        
        .stRadio > label > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
        }}
        
        /* Sliders */
        .stSlider > div > div > div > div {{
            background: {cores['background']} !important;
        }}
        
        /* Date inputs */
        .stDateInput > div > div > input {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        /* Time inputs */
        .stTimeInput > div > div > input {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        /* File uploader */
        .stFileUploader > div > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
        }}
        
        /* Multiselect */
        .stMultiSelect > div > div {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
        }}
        
        /* Textarea */
        .stTextArea > div > div > textarea {{
            background: {cores['background']} !important;
            border: 1px solid {cores['border']} !important;
            border-radius: 8px !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stTextArea > div > div > textarea:focus {{
            border-color: {cores['primary']} !important;
            box-shadow: 0 0 0 1px {cores['primary']} !important;
        }}
        
        .stDataFrame {{
            background: {cores['surface']};
            border: 1px solid {cores['border']};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .stDataFrame table {{
            background: transparent !important;
            color: {cores['text_primary']} !important;
        }}
        
        .stDataFrame th {{
            background: {cores['border']} !important;
            color: {cores['text_primary']} !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            border-bottom: 1px solid {cores['surface']} !important;
            padding: 1rem !important;
        }}
        
        .stDataFrame td {{
            background: transparent !important;
            color: {cores['text_primary']} !important;
            border-bottom: 1px solid {cores['border']} !important;
            font-size: 0.875rem !important;
            padding: 0.75rem 1rem !important;
        }}
        
        .stDataFrame tr:hover td {{
            background: rgba(192, 192, 192, 0.1) !important;
        }}
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{visibility: hidden;}}
        
        .stApp > div {{
            animation: fadeIn 0.6s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {cores['background']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {cores['border']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {cores['primary']};
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard premium"""
    configurar_pagina()
    aplicar_css_premium()
    
    # Header principal premium
    st.markdown(f'<div class="page-header">FOX SA Investment Board</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size: 1.1rem; color: #C0C0C0; font-weight: 400; margin-bottom: 2rem; text-align: left;">Comprehensive agribusiness dashboard for institutional investors</p>', unsafe_allow_html=True)
    
    # Controles da sidebar
    ano_selecionado, tipo_visualizacao = criar_sidebar_controles_premium()
    
    # Carregar dados
    dados_eda = carregar_dados_eda()
    dados_financeiros = carregar_dados_financeiros()
    
    # Menu de navegação
    st.sidebar.markdown('<div class="sidebar-header">Navigation</div>', unsafe_allow_html=True)
    
    menu_options = [
        "Consolidated View",
        "Geographic Map",
        "LTV Analysis", 
        "Commodity Analysis",
        "Logistics Overview",
        "Advisory Services",
        "Financial Analysis",
        "Administration"
    ]
    
    opcao = st.sidebar.selectbox("Select view:", menu_options)
    
    # Roteamento de páginas
    if opcao == "Consolidated View":
        pagina_visao_consolidada_premium(dados_eda, dados_financeiros, ano_selecionado)
    
    elif opcao == "Geographic Map":
        pagina_mapa_goias_premium(dados_eda)
    
    elif opcao == "LTV Analysis":
        pagina_analise_ltv_premium(dados_eda)
    
    elif opcao == "Commodity Analysis":
        pagina_analise_commodities_premium(dados_eda, ano_selecionado)
    
    elif opcao == "Logistics Overview":
        st.markdown('<div class="page-header">Logistics Overview</div>', unsafe_allow_html=True)
        st.info("Logistics analysis page - Coming soon!")
    
    elif opcao == "Advisory Services":
        st.markdown('<div class="page-header">Advisory Services</div>', unsafe_allow_html=True)
        st.info("Advisory services analysis page - Coming soon!")
    
    elif opcao == "Financial Analysis":
        st.markdown('<div class="page-header">Financial Analysis</div>', unsafe_allow_html=True)
        st.info("Financial analysis page - Coming soon!")
    
    elif opcao == "Administration":
        st.markdown('<div class="page-header">Administration</div>', unsafe_allow_html=True)
        st.info("Administration page - Coming soon!")

if __name__ == "__main__":
    main()

