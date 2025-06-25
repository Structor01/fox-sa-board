"""
Página de Contratos Reais - Dados do MongoDB orderv2
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from mongodb_connector import load_contracts_data, load_financial_summary, load_monthly_performance

def pagina_contratos_reais(tema='escuro'):
    """Página principal dos contratos reais"""
    
    # Título da página
    st.markdown("## 📋 Contratos Reais - OrderV2")
    st.markdown("*Dados em tempo real do MongoDB da FOX SA*")
    
    # Carregar dados
    with st.spinner("Carregando dados dos contratos..."):
        try:
            df_contratos = load_contracts_data(limit=1000)
            resumo_financeiro = load_financial_summary()
            
            if df_contratos.empty:
                st.error("❌ Não foi possível carregar os dados dos contratos")
                st.info("Verifique a conexão com o MongoDB")
                return
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            return
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Filtro por grão
        graos_disponiveis = ['Todos'] + sorted(df_contratos['grainName'].unique().tolist())
        grao_selecionado = st.selectbox("🌾 Grão", graos_disponiveis)
    
    with col2:
        # Filtro por status
        status_disponiveis = ['Todos'] + sorted(df_contratos['status'].unique().tolist())
        status_selecionado = st.selectbox("📊 Status", status_disponiveis)
    
    with col3:
        # Filtro por tipo de operação
        tipos_operacao = ['Todos'] + sorted(df_contratos['tipoOperacao'].unique().tolist())
        tipo_selecionado = st.selectbox("🔄 Operação", tipos_operacao)
    
    with col4:
        # Filtro por período
        periodo_opcoes = ['Últimos 30 dias', 'Últimos 90 dias', 'Último ano', 'Todos']
        periodo_selecionado = st.selectbox("📅 Período", periodo_opcoes)
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros_contratos(df_contratos, grao_selecionado, 
                                          status_selecionado, tipo_selecionado, 
                                          periodo_selecionado)
    
    # KPIs principais
    exibir_kpis_contratos(df_filtrado, tema)
    
    st.divider()
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de contratos por mês
        criar_grafico_contratos_mensais(df_filtrado, tema)
    
    with col2:
        # Gráfico de valor por grão
        criar_grafico_valor_por_grao(df_filtrado, tema)
    
    # Segunda linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Status dos contratos
        criar_grafico_status_contratos(df_filtrado, tema)
    
    with col2:
        # Modalidade de frete
        criar_grafico_modalidade_frete(df_filtrado, tema)
    
    st.divider()
    
    # Tabela detalhada dos contratos
    exibir_tabela_contratos(df_filtrado)
    
    # Análises avançadas
    st.divider()
    exibir_analises_avancadas(df_filtrado, tema)

def aplicar_filtros_contratos(df, grao, status, tipo_operacao, periodo):
    """Aplica filtros aos dados dos contratos"""
    df_filtrado = df.copy()
    
    # Filtro por grão
    if grao != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['grainName'] == grao]
    
    # Filtro por status
    if status != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['status'] == status]
    
    # Filtro por tipo de operação
    if tipo_operacao != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipoOperacao'] == tipo_operacao]
    
    # Filtro por período
    hoje = datetime.now()
    if periodo == 'Últimos 30 dias':
        data_limite = hoje - timedelta(days=30)
        df_filtrado = df_filtrado[df_filtrado['closeDate'] >= data_limite]
    elif periodo == 'Últimos 90 dias':
        data_limite = hoje - timedelta(days=90)
        df_filtrado = df_filtrado[df_filtrado['closeDate'] >= data_limite]
    elif periodo == 'Último ano':
        data_limite = hoje - timedelta(days=365)
        df_filtrado = df_filtrado[df_filtrado['closeDate'] >= data_limite]
    
    return df_filtrado

def exibir_kpis_contratos(df, tema):
    """Exibe KPIs principais dos contratos"""
    
    if df.empty:
        st.warning("⚠️ Nenhum contrato encontrado com os filtros aplicados")
        return
    
    # Calcular métricas
    total_contratos = len(df)
    valor_total = df['valorTotal'].sum()
    volume_total = df['amount'].sum()
    preco_medio = df['bagPrice'].mean()
    
    # Comparação com período anterior (últimos 30 dias vs 30 dias anteriores)
    hoje = datetime.now()
    data_30_dias = hoje - timedelta(days=30)
    data_60_dias = hoje - timedelta(days=60)
    
    df_atual = df[df['closeDate'] >= data_30_dias]
    df_anterior = df[(df['closeDate'] >= data_60_dias) & (df['closeDate'] < data_30_dias)]
    
    # Calcular variações
    var_contratos = calcular_variacao(len(df_atual), len(df_anterior))
    var_valor = calcular_variacao(df_atual['valorTotal'].sum(), df_anterior['valorTotal'].sum())
    var_volume = calcular_variacao(df_atual['amount'].sum(), df_anterior['amount'].sum())
    var_preco = calcular_variacao(df_atual['bagPrice'].mean(), df_anterior['bagPrice'].mean())
    
    # Exibir KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total de Contratos",
            value=f"{total_contratos:,}",
            delta=f"{var_contratos:+.1f}%"
        )
    
    with col2:
        st.metric(
            label="💰 Valor Total",
            value=f"R$ {valor_total/1_000_000:.1f}M",
            delta=f"{var_valor:+.1f}%"
        )
    
    with col3:
        st.metric(
            label="📦 Volume Total",
            value=f"{volume_total:,.0f} sacas",
            delta=f"{var_volume:+.1f}%"
        )
    
    with col4:
        st.metric(
            label="💵 Preço Médio",
            value=f"R$ {preco_medio:.2f}/saca",
            delta=f"{var_preco:+.1f}%"
        )

def calcular_variacao(atual, anterior):
    """Calcula variação percentual"""
    if anterior == 0 or pd.isna(anterior):
        return 0
    return ((atual - anterior) / anterior) * 100

def criar_grafico_contratos_mensais(df, tema):
    """Cria gráfico de contratos por mês"""
    
    if df.empty:
        st.info("Sem dados para exibir")
        return
    
    # Agrupar por mês
    df_mensal = df.groupby(df['closeDate'].dt.to_period('M')).agg({
        'orderId': 'count',
        'valorTotal': 'sum'
    }).reset_index()
    
    df_mensal['mes'] = df_mensal['closeDate'].astype(str)
    df_mensal = df_mensal.sort_values('closeDate')
    
    # Criar gráfico
    fig = go.Figure()
    
    # Barras para número de contratos
    fig.add_trace(go.Bar(
        x=df_mensal['mes'],
        y=df_mensal['orderId'],
        name='Número de Contratos',
        marker_color='#3B82F6',
        yaxis='y'
    ))
    
    # Linha para valor total
    fig.add_trace(go.Scatter(
        x=df_mensal['mes'],
        y=df_mensal['valorTotal'] / 1_000_000,
        mode='lines+markers',
        name='Valor Total (R$ M)',
        line=dict(color='#EF4444', width=3),
        yaxis='y2'
    ))
    
    # Layout
    fig.update_layout(
        title="📈 Contratos e Valor por Mês",
        xaxis_title="Mês",
        yaxis=dict(title="Número de Contratos", side="left"),
        yaxis2=dict(title="Valor Total (R$ Milhões)", side="right", overlaying="y"),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        paper_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        font_color='white' if tema == 'escuro' else 'black'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_valor_por_grao(df, tema):
    """Cria gráfico de valor por tipo de grão"""
    
    if df.empty:
        st.info("Sem dados para exibir")
        return
    
    # Agrupar por grão
    df_graos = df.groupby('grainName').agg({
        'valorTotal': 'sum',
        'amount': 'sum',
        'orderId': 'count'
    }).reset_index()
    
    df_graos = df_graos.sort_values('valorTotal', ascending=True)
    
    # Criar gráfico
    fig = px.bar(
        df_graos,
        x='valorTotal',
        y='grainName',
        orientation='h',
        title="💰 Valor Total por Grão",
        labels={'valorTotal': 'Valor Total (R$)', 'grainName': 'Grão'},
        color='valorTotal',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        paper_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        font_color='white' if tema == 'escuro' else 'black'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_status_contratos(df, tema):
    """Cria gráfico de status dos contratos"""
    
    if df.empty:
        st.info("Sem dados para exibir")
        return
    
    # Contar por status
    status_counts = df['status'].value_counts()
    
    # Cores por status
    cores_status = {
        'Concluído': '#10B981',
        'Em Andamento': '#3B82F6',
        'Ativo': '#F59E0B',
        'Vencido': '#EF4444',
        'Próximo ao Vencimento': '#F97316'
    }
    
    cores = [cores_status.get(status, '#6B7280') for status in status_counts.index]
    
    # Criar gráfico
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="📊 Status dos Contratos",
        color_discrete_sequence=cores
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        paper_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        font_color='white' if tema == 'escuro' else 'black'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def criar_grafico_modalidade_frete(df, tema):
    """Cria gráfico de modalidade de frete"""
    
    if df.empty:
        st.info("Sem dados para exibir")
        return
    
    # Contar por modalidade
    frete_counts = df['modalidadeFrete'].value_counts()
    
    # Criar gráfico
    fig = px.bar(
        x=frete_counts.index,
        y=frete_counts.values,
        title="🚚 Modalidade de Frete",
        labels={'x': 'Modalidade', 'y': 'Número de Contratos'},
        color=frete_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        paper_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        font_color='white' if tema == 'escuro' else 'black'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def exibir_tabela_contratos(df):
    """Exibe tabela detalhada dos contratos"""
    
    st.markdown("### 📋 Detalhes dos Contratos")
    
    if df.empty:
        st.info("Nenhum contrato encontrado com os filtros aplicados")
        return
    
    # Selecionar colunas para exibição
    colunas_exibicao = [
        'orderId', 'closeDate', 'grainName', 'amount', 'bagPrice', 
        'valorTotal', 'status', 'tipoOperacao', 'modalidadeFrete',
        'deliveryDeadline', 'deliveryDeadlineEnd', 'buyerName', 'sellerName'
    ]
    
    df_tabela = df[colunas_exibicao].copy()
    
    # Formatação
    df_tabela['closeDate'] = df_tabela['closeDate'].dt.strftime('%d/%m/%Y')
    df_tabela['deliveryDeadline'] = df_tabela['deliveryDeadline'].dt.strftime('%d/%m/%Y')
    df_tabela['deliveryDeadlineEnd'] = df_tabela['deliveryDeadlineEnd'].dt.strftime('%d/%m/%Y')
    df_tabela['valorTotal'] = df_tabela['valorTotal'].apply(lambda x: f"R$ {x:,.2f}")
    df_tabela['bagPrice'] = df_tabela['bagPrice'].apply(lambda x: f"R$ {x:.2f}")
    df_tabela['amount'] = df_tabela['amount'].apply(lambda x: f"{x:,.0f}")
    
    # Renomear colunas
    df_tabela.columns = [
        'ID Pedido', 'Data Fechamento', 'Grão', 'Quantidade', 'Preço/Saca',
        'Valor Total', 'Status', 'Operação', 'Frete',
        'Entrega Início', 'Entrega Fim', 'Comprador', 'Vendedor'
    ]
    
    # Exibir tabela
    st.dataframe(
        df_tabela,
        use_container_width=True,
        height=400
    )
    
    # Botão para download
    csv = df_tabela.to_csv(index=False)
    st.download_button(
        label="📥 Baixar dados em CSV",
        data=csv,
        file_name=f"contratos_fox_sa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def exibir_analises_avancadas(df, tema):
    """Exibe análises avançadas dos contratos"""
    
    st.markdown("### 📊 Análises Avançadas")
    
    if df.empty:
        st.info("Sem dados para análises avançadas")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análise de prazo de entrega
        st.markdown("#### ⏰ Análise de Prazos")
        
        prazo_stats = {
            'Prazo médio para entrega': f"{df['diasParaEntrega'].mean():.0f} dias",
            'Contratos vencidos': f"{len(df[df['diasParaEntrega'] < 0])} ({len(df[df['diasParaEntrega'] < 0])/len(df)*100:.1f}%)",
            'Próximos ao vencimento': f"{len(df[df['diasParaEntrega'].between(0, 30)])} ({len(df[df['diasParaEntrega'].between(0, 30)])/len(df)*100:.1f}%)",
            'Duração média da janela': f"{df['duracaoJanelaEntrega'].mean():.0f} dias"
        }
        
        for label, valor in prazo_stats.items():
            st.metric(label, valor)
    
    with col2:
        # Análise financeira
        st.markdown("#### 💰 Análise Financeira")
        
        financeiro_stats = {
            'Ticket médio': f"R$ {df['valorTotal'].mean():,.2f}",
            'Maior contrato': f"R$ {df['valorTotal'].max():,.2f}",
            'Menor contrato': f"R$ {df['valorTotal'].min():,.2f}",
            'Taxa financeira média': f"{df['financialRate'].mean():.2f}%"
        }
        
        for label, valor in financeiro_stats.items():
            st.metric(label, valor)
    
    # Gráfico de distribuição de valores
    st.markdown("#### 📈 Distribuição de Valores dos Contratos")
    
    fig = px.histogram(
        df,
        x='valorTotal',
        nbins=20,
        title="Distribuição de Valores dos Contratos",
        labels={'valorTotal': 'Valor do Contrato (R$)', 'count': 'Frequência'}
    )
    
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        paper_bgcolor='rgba(0,0,0,0)' if tema == 'escuro' else 'white',
        font_color='white' if tema == 'escuro' else 'black'
    )
    
    st.plotly_chart(fig, use_container_width=True)

