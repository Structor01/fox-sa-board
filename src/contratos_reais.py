"""
Página de Contratos Reais - Dados do MongoDB orderv2
"""

import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from mongodb_connector import load_contracts_data, load_financial_summary, load_monthly_performance

def pagina_contratos_reais(tema='escuro', filtros_globais=None):
    """Página principal dos contratos reais"""
    
    # Título da página
    st.markdown("## Contratos")
    st.markdown("*Dados em tempo real do MongoDB da FOX SA*")
    
    # Carregar dados
    with st.spinner("Carregando dados dos contratos..."):
        try:
            df_contratos = load_contracts_data(limit=1000)
            resumo_financeiro = load_financial_summary()
            
            if df_contratos.empty:
                st.error("Não foi possível carregar os dados dos contratos")
                st.info("Verifique a conexão com o MongoDB")
                return
                
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            return
    
    # Aplicar filtros globais se fornecidos
    if filtros_globais:
        # Importar função de aplicar filtros globais
        from app import aplicar_filtros_globais
        df_filtrado = aplicar_filtros_globais(df_contratos, filtros_globais)
        
        # Mostrar informações sobre filtros aplicados
        filtros_ativos = [k for k, v in filtros_globais.items() if v != 'Todos']
        if filtros_ativos:
            st.info(f"Filtros aplicados: {', '.join([f'{k}: {v}' for k, v in filtros_globais.items() if v != 'Todos'])}")
    else:
        df_filtrado = df_contratos
    
    # KPIs principais
    exibir_kpis_contratos(df_filtrado, tema)
    
    st.divider()
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de contratos por mês
        criar_grafico_contratos_mensais(df_filtrado, tema)
    
    with col2:
        # Gráfico de valor por produto
        fig_valor_grao = criar_grafico_valor_por_grao(df_filtrado, tema)
        if fig_valor_grao:
            st.plotly_chart(fig_valor_grao, use_container_width=True)
    
    # Segunda linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Status dos contratos
        criar_grafico_status_contratos(df_filtrado, tema)
    
    with col2:
        # Modalidade de frete
        criar_grafico_modalidade_frete(df_filtrado, tema)
    
    # Mapa de localizações
    st.markdown("---")
    st.subheader("📍 Mapa de Localizações")
    
    # Filtrar apenas Supply e Originação para o mapa
    df_mapa = df_filtrado[df_filtrado['tipoOperacao'].isin(['Supply', 'Originação'])]
    
    if not df_mapa.empty:
        fig_mapa = criar_mapa_contratos(df_mapa, tema)
        if fig_mapa:
            st.plotly_chart(fig_mapa, use_container_width=True)
            
            # Estatísticas do mapa
            col1, col2, col3 = st.columns(3)
            with col1:
                supply_count = len(df_mapa[df_mapa['tipoOperacao'] == 'Supply'])
                st.metric("🔴 Pontos Supply", supply_count)
            with col2:
                originacao_count = len(df_mapa[df_mapa['tipoOperacao'] == 'Originação'])
                st.metric("🔵 Pontos Originação", originacao_count)
            with col3:
                total_volume = df_mapa['amount'].sum()
                st.metric("📦 Volume Total", f"{total_volume:,.0f} un.")
    else:
        st.info("📍 Nenhum contrato de Supply ou Originação encontrado para exibir no mapa.")
    
    st.divider()
    
    # Tabela detalhada dos contratos
    exibir_tabela_contratos(df_filtrado)
    
    # Análises avançadas
    st.divider()
    exibir_analises_avancadas(df_filtrado, tema)

def aplicar_filtros_contratos(df, grao, status, tipo_operacao, ano):
    """Aplica filtros aos dados dos contratos"""
    df_filtrado = df.copy()
    
    # Filtro por produto
    if grao != 'Todos':
        if 'grainName' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['grainName'] == grao]
        else:
            st.warning("⚠️ Campo grainName não encontrado. Filtro por produto não aplicado.")
    
    # Filtro por status
    if status != 'Todos':
        if 'status' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['status'] == status]
        else:
            st.warning("⚠️ Campo status não encontrado. Filtro por status não aplicado.")
    
    # Filtro por tipo de operação
    if tipo_operacao != 'Todos':
        if tipo_operacao == 'Supply':
            # Supply: isBuying: false, isGrain: true
            if 'isGrain' in df_filtrado.columns and 'isBuying' in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    (df_filtrado['isBuying'] == False) & 
                    (df_filtrado['isGrain'] == True)
                ]
            else:
                st.warning("⚠️ Campos isGrain/isBuying não encontrados. Filtro Supply não aplicado.")
        elif tipo_operacao == 'Originação':
            # Originação: isBuying: true, isGrain: true
            if 'isGrain' in df_filtrado.columns and 'isBuying' in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    (df_filtrado['isBuying'] == True) & 
                    (df_filtrado['isGrain'] == True)
                ]
            else:
                st.warning("⚠️ Campos isGrain/isBuying não encontrados. Filtro Originação não aplicado.")
        elif tipo_operacao == 'Frete':
            # Frete: isFreight: true
            if 'isFreight' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isFreight'] == True]
            else:
                st.warning("⚠️ Campo isFreight não encontrado. Filtro Frete não aplicado.")
        elif tipo_operacao == 'Clube FX':
            # Clube FX: isService: true
            if 'isService' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['isService'] == True]
            else:
                st.warning("⚠️ Campo isService não encontrado. Filtro Clube FX não aplicado.")
    
    # Filtro por ano
    if ano and ano != 'Todos':
        try:
            ano_int = int(ano)
            df_filtrado = df_filtrado[df_filtrado['closeDate'].dt.year == ano_int]
        except (ValueError, TypeError):
            # Se não conseguir converter para int, ignora o filtro
            st.warning(f"⚠️ Valor de ano inválido: {ano} (tipo: {type(ano)})")
            pass
    
    return df_filtrado

def exibir_kpis_contratos(df, tema):
    """Exibe KPIs principais dos contratos"""
    
    if df.empty:
        st.warning("⚠️ Nenhum contrato encontrado com os filtros aplicados")
        return
    
    # Calcular métricas
    total_contratos = len(df)
    valor_total = df['valorTotal'].sum()
    
    # Separar volumes por tipo de operação
    volume_comprado = df[df['isBuying'] == True]['amount'].sum()
    volume_vendido = df[df['isBuying'] == False]['amount'].sum()
    
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
    
    # Variações de volume por tipo
    var_volume_comprado = calcular_variacao(
        df_atual[df_atual['isBuying'] == True]['amount'].sum(),
        df_anterior[df_anterior['isBuying'] == True]['amount'].sum()
    )
    var_volume_vendido = calcular_variacao(
        df_atual[df_atual['isBuying'] == False]['amount'].sum(),
        df_anterior[df_anterior['isBuying'] == False]['amount'].sum()
    )
    
    var_preco = calcular_variacao(df_atual['bagPrice'].mean(), df_anterior['bagPrice'].mean())
    
    # Exibir KPIs em 5 colunas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📋 Total de Contratos",
            f"{total_contratos:,}",
            delta=f"{var_contratos:+.1f}%" if var_contratos != 0 else None
        )
    
    with col2:
        st.metric(
            "💰 Valor Total",
            f"R$ {valor_total:,.0f}",
            delta=f"{var_valor:+.1f}%" if var_valor != 0 else None
        )
    
    with col3:
        st.metric(
            "📈 Volume Comprado",
            f"{volume_comprado:,.0f} un.",
            delta=f"{var_volume_comprado:+.1f}%" if var_volume_comprado != 0 else None
        )
    
    with col4:
        st.metric(
            "📉 Volume Vendido", 
            f"{volume_vendido:,.0f} un.",
            delta=f"{var_volume_vendido:+.1f}%" if var_volume_vendido != 0 else None
        )
    
    with col5:
        st.metric(
            "💵 Preço Médio",
            f"R$ {preco_medio:.2f}/un.",
            delta=f"{var_preco:+.1f}%" if var_preco != 0 else None
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
        'deliveryDeadline', 'deliveryDeadlineEnd', 'buyerName', 'sellerName',
        'fromCity', 'fromState', 'fromLat', 'fromLng',
        'toCity', 'toState', 'toLat', 'toLng'
    ]
    
    # Verificar se as colunas existem no DataFrame
    colunas_existentes = [col for col in colunas_exibicao if col in df.columns]
    df_tabela = df[colunas_existentes].copy()
    
    # Formatação
    if 'closeDate' in df_tabela.columns:
        df_tabela['closeDate'] = df_tabela['closeDate'].dt.strftime('%d/%m/%Y')
    if 'deliveryDeadline' in df_tabela.columns:
        df_tabela['deliveryDeadline'] = df_tabela['deliveryDeadline'].dt.strftime('%d/%m/%Y')
    if 'deliveryDeadlineEnd' in df_tabela.columns:
        df_tabela['deliveryDeadlineEnd'] = df_tabela['deliveryDeadlineEnd'].dt.strftime('%d/%m/%Y')
    if 'valorTotal' in df_tabela.columns:
        df_tabela['valorTotal'] = df_tabela['valorTotal'].apply(lambda x: f"R$ {x:,.2f}")
    if 'bagPrice' in df_tabela.columns:
        df_tabela['bagPrice'] = df_tabela['bagPrice'].apply(lambda x: f"R$ {x:.2f}")
    if 'amount' in df_tabela.columns:
        df_tabela['amount'] = df_tabela['amount'].apply(lambda x: f"{x:,.0f}")
    
    # Formatação das coordenadas
    for coord_col in ['fromLat', 'fromLng', 'toLat', 'toLng']:
        if coord_col in df_tabela.columns:
            df_tabela[coord_col] = df_tabela[coord_col].apply(
                lambda x: f"{x:.6f}" if pd.notna(x) else "N/A"
            )
    
    # Renomear colunas
    rename_dict = {
        'orderId': 'ID Pedido',
        'closeDate': 'Data Fechamento',
        'grainName': 'Produto',
        'amount': 'Quantidade',
        'bagPrice': 'Preço/Un.',
        'valorTotal': 'Valor Total',
        'status': 'Status',
        'tipoOperacao': 'Operação',
        'modalidadeFrete': 'Frete',
        'deliveryDeadline': 'Entrega Início',
        'deliveryDeadlineEnd': 'Entrega Fim',
        'buyerName': 'Comprador',
        'sellerName': 'Vendedor',
        'fromCity': 'Cidade Origem',
        'fromState': 'Estado Origem',
        'fromLat': 'Lat Origem',
        'fromLng': 'Lng Origem',
        'toCity': 'Cidade Destino',
        'toState': 'Estado Destino',
        'toLat': 'Lat Destino',
        'toLng': 'Lng Destino'
    }
    
    # Aplicar renomeação apenas para colunas existentes
    df_tabela.columns = [rename_dict.get(col, col) for col in df_tabela.columns]
    
    # Converter ObjectIds para strings em todas as colunas object
    for col in df_tabela.columns:
        if df_tabela[col].dtype == 'object':
            df_tabela[col] = df_tabela[col].apply(lambda x: str(x) if x is not None else 'N/A')
    
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


def criar_mapa_contratos(df, tema='plotly'):
    """Cria mapa com localizações dos contratos de Supply e Originação"""
    try:
        import plotly.express as px
        import pandas as pd
        import numpy as np
        
        # Preparar dados para o mapa
        map_data = []
        
        for _, row in df.iterrows():
            tipo_operacao = row.get('tipoOperacao', '')
            
            # Para Supply, usar destino (to)
            if tipo_operacao == 'Supply' and row.get('toLocation') is not None:
                location = row['toLocation']
                if isinstance(location, dict) and 'coordinates' in location:
                    coords = location['coordinates']
                    if len(coords) >= 2 and pd.notna(coords[0]) and pd.notna(coords[1]):
                        # Garantir que são números válidos
                        lat = float(coords[1]) if coords[1] is not None else None
                        lon = float(coords[0]) if coords[0] is not None else None
                        quantidade = float(row.get('amount', 0)) if pd.notna(row.get('amount', 0)) else 0
                        valor = float(row.get('valorTotal', 0)) if pd.notna(row.get('valorTotal', 0)) else 0
                        preco = float(row.get('bagPrice', 0)) if pd.notna(row.get('bagPrice', 0)) else 0
                        
                        if lat is not None and lon is not None:
                            map_data.append({
                                'lat': lat,
                                'lon': lon,
                                'quantidade': quantidade,
                                'valor': valor,
                                'tipo': 'Supply',
                                'cidade': str(row.get('toCity', 'Não informado')),
                                'estado': str(row.get('toState', 'Não informado')),
                                'produto': str(row.get('grainName', 'Não informado')),
                                'preco': preco
                            })
            
            # Para Originação, usar origem (from)
            elif tipo_operacao == 'Originação' and row.get('fromLocation') is not None:
                location = row['fromLocation']
                if isinstance(location, dict) and 'coordinates' in location:
                    coords = location['coordinates']
                    if len(coords) >= 2 and pd.notna(coords[0]) and pd.notna(coords[1]):
                        # Garantir que são números válidos
                        lat = float(coords[1]) if coords[1] is not None else None
                        lon = float(coords[0]) if coords[0] is not None else None
                        quantidade = float(row.get('amount', 0)) if pd.notna(row.get('amount', 0)) else 0
                        valor = float(row.get('valorTotal', 0)) if pd.notna(row.get('valorTotal', 0)) else 0
                        preco = float(row.get('bagPrice', 0)) if pd.notna(row.get('bagPrice', 0)) else 0
                        
                        if lat is not None and lon is not None:
                            map_data.append({
                                'lat': lat,
                                'lon': lon,
                                'quantidade': quantidade,
                                'valor': valor,
                                'tipo': 'Originação',
                                'cidade': str(row.get('fromCity', 'Não informado')),
                                'estado': str(row.get('fromState', 'Não informado')),
                                'produto': str(row.get('grainName', 'Não informado')),
                                'preco': preco
                            })
        
        if not map_data:
            st.info("📍 Nenhum contrato com localização disponível para exibir no mapa.")
            return None
        
        # Converter para DataFrame
        df_map = pd.DataFrame(map_data)
        
        # Garantir que todos os valores numéricos são válidos
        df_map['lat'] = pd.to_numeric(df_map['lat'], errors='coerce')
        df_map['lon'] = pd.to_numeric(df_map['lon'], errors='coerce')
        df_map['quantidade'] = pd.to_numeric(df_map['quantidade'], errors='coerce').fillna(0)
        df_map['valor'] = pd.to_numeric(df_map['valor'], errors='coerce').fillna(0)
        df_map['preco'] = pd.to_numeric(df_map['preco'], errors='coerce').fillna(0)
        
        # Remover linhas com coordenadas inválidas
        df_map = df_map.dropna(subset=['lat', 'lon'])
        
        if df_map.empty:
            st.info("📍 Nenhum contrato com coordenadas válidas para exibir no mapa.")
            return None
        
        # Agregar por localização para evitar sobreposição
        df_map_agg = df_map.groupby(['lat', 'lon', 'cidade', 'estado', 'tipo']).agg({
            'quantidade': 'sum',
            'valor': 'sum',
            'produto': lambda x: ', '.join(x.unique()),
            'preco': 'mean'
        }).reset_index()
        
        # Garantir que valores agregados são serializáveis
        df_map_agg['quantidade'] = df_map_agg['quantidade'].astype(float)
        df_map_agg['valor'] = df_map_agg['valor'].astype(float)
        df_map_agg['preco'] = df_map_agg['preco'].astype(float)
        df_map_agg['lat'] = df_map_agg['lat'].astype(float)
        df_map_agg['lon'] = df_map_agg['lon'].astype(float)
        
        # Criar o mapa
        fig = px.scatter_mapbox(
            df_map_agg,
            lat='lat',
            lon='lon',
            size='quantidade',
            color='tipo',
            hover_name='cidade',
            hover_data={
                'estado': True,
                'quantidade': ':,',
                'valor': ':,.2f',
                'produto': True,
                'preco': ':,.2f',
                'lat': False,
                'lon': False
            },
            color_discrete_map={
                'Supply': '#FF6B6B',
                'Originação': '#4ECDC4'
            },
            size_max=50,
            zoom=4,
            center={'lat': -15.7801, 'lon': -47.9292},  # Centro do Brasil
            mapbox_style='open-street-map',
            title='📍 Mapa de Contratos - Supply e Originação'
        )
        
        # Configurar layout
        fig.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erro ao criar mapa: {str(e)}")
        return None

