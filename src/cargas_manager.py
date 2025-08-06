#!/usr/bin/env python3
"""
Módulo de Gestão de Cargas - Fox SA
Inclui tabela de cargas com coluna "Frete por Saca"
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

def criar_dados_cargas():
    """Criar dados simulados de cargas com frete por saca"""
    
    cargas_data = {
        'ID': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008', 'C009', 'C010'],
        'Vendedor': [
            'João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Lima', 'Carlos Souza',
            'Lucia Ferreira', 'Roberto Alves', 'Fernanda Rocha', 'Paulo Mendes', 'Sandra Oliveira'
        ],
        'Origem': [
            'Fazenda Santa Rita - GO', 'Cooperativa Regional - MT', 'Sítio Boa Vista - MS',
            'Fazenda Esperança - GO', 'Agropecuária Silva - MT', 'Fazenda Progresso - GO',
            'Cooperativa Central - MS', 'Fazenda Vitória - GO', 'Sítio Palmeiras - MT',
            'Fazenda Horizonte - MS'
        ],
        'Destino': [
            'Terminal Santos - SP', 'Porto Paranaguá - PR', 'Terminal Santos - SP',
            'Porto Rio Grande - RS', 'Terminal Santos - SP', 'Porto Paranaguá - PR',
            'Terminal Santos - SP', 'Porto Rio Grande - RS', 'Porto Paranaguá - PR',
            'Terminal Santos - SP'
        ],
        'Produto': [
            'Soja', 'Milho', 'Soja', 'Soja', 'Milho', 'Soja',
            'Milho', 'Soja', 'Milho', 'Soja'
        ],
        'Volume (sacas)': [2500, 1800, 3200, 1500, 2800, 2100, 3500, 1900, 2200, 2700],
        'Distância (km)': [920, 680, 1080, 1200, 1150, 750, 1050, 1180, 720, 980],
        'Frete Total (R$)': [9200, 6120, 12960, 7200, 11200, 7350, 13650, 8740, 7480, 10530],
        'Frete por Saca (R$)': [3.68, 3.40, 4.05, 4.80, 4.00, 3.50, 3.90, 4.60, 3.40, 3.90],
        'Status': [
            'Em Trânsito', 'Entregue', 'Carregando', 'Agendado', 'Em Trânsito',
            'Entregue', 'Carregando', 'Agendado', 'Em Trânsito', 'Entregue'
        ],
        'Data Carregamento': [
            '2024-06-25', '2024-06-23', '2024-06-26', '2024-06-28', '2024-06-24',
            '2024-06-22', '2024-06-27', '2024-06-29', '2024-06-21', '2024-06-30'
        ],
        'Transportadora': [
            'Fox Log', 'Parceiro A', 'Fox Log', 'Parceiro B', 'Parceiro A',
            'Fox Log', 'Parceiro C', 'Fox Log', 'Parceiro A', 'Fox Log'
        ],
        'Motorista': [
            'José Santos', 'Carlos Lima', 'Pedro Silva', 'João Costa', 'Maria Souza',
            'Ana Ferreira', 'Roberto Alves', 'Lucia Rocha', 'Paulo Mendes', 'Sandra Oliveira'
        ],
        'Placa': [
            'ABC-1234', 'DEF-5678', 'GHI-9012', 'JKL-3456', 'MNO-7890',
            'PQR-1357', 'STU-2468', 'VWX-9753', 'YZA-8642', 'BCD-1975'
        ]
    }
    
    return pd.DataFrame(cargas_data)

def exibir_metricas_cargas(df):
    """Exibir métricas principais das cargas"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_cargas = len(df)
        st.metric("Total de Cargas", total_cargas, delta="+3 hoje")
    
    with col2:
        volume_total = df['Volume (sacas)'].sum()
        st.metric("Volume Total", f"{volume_total:,} sacas", delta="+1.2k sacas")
    
    with col3:
        frete_medio = df['Frete por Saca (R$)'].mean()
        st.metric("Frete Médio/Saca", f"R$ {frete_medio:.2f}", delta="-R$ 0.15")
    
    with col4:
        frete_total = df['Frete Total (R$)'].sum()
        st.metric("Frete Total", f"R$ {frete_total:,.0f}".replace(',', '.'), delta="+R$ 5.2k")
    
    with col5:
        em_transito = len(df[df['Status'] == 'Em Trânsito'])
        st.metric("Em Trânsito", em_transito, delta=f"{em_transito}/{total_cargas}")

def aplicar_filtros_cargas(df):
    """Aplicar filtros na tabela de cargas"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_options = ['Todos'] + list(df['Status'].unique())
        status_filter = st.selectbox("Status", status_options)
    
    with col2:
        transp_options = ['Todas'] + list(df['Transportadora'].unique())
        transp_filter = st.selectbox("Transportadora", transp_options)
    
    with col3:
        produto_options = ['Todos'] + list(df['Produto'].unique())
        produto_filter = st.selectbox("Produto", produto_options)
    
    with col4:
        ordenar_options = [
            'Frete por Saca (R$)', 'Volume (sacas)', 'Data Carregamento', 
            'Distância (km)', 'Frete Total (R$)'
        ]
        ordenar_por = st.selectbox("Ordenar por", ordenar_options)
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if status_filter != 'Todos':
        df_filtered = df_filtered[df_filtered['Status'] == status_filter]
    
    if transp_filter != 'Todas':
        df_filtered = df_filtered[df_filtered['Transportadora'] == transp_filter]
    
    if produto_filter != 'Todos':
        df_filtered = df_filtered[df_filtered['Produto'] == produto_filter]
    
    # Ordenar
    ascending = False if ordenar_por in ['Frete por Saca (R$)', 'Volume (sacas)', 'Frete Total (R$)'] else True
    df_filtered = df_filtered.sort_values(ordenar_por, ascending=ascending)
    
    return df_filtered

def destacar_frete_por_saca(df):
    """Aplicar destaque visual na coluna Frete por Saca"""
    
    def highlight_frete_column(row):
        styles = [''] * len(row)
        # Destacar a coluna "Frete por Saca (R$)" em amarelo claro
        try:
            frete_idx = df.columns.get_loc('Frete por Saca (R$)')
            styles[frete_idx] = 'background-color: #FFFACD; font-weight: bold; color: #B8860B;'
        except:
            pass
        return styles
    
    return df.style.apply(highlight_frete_column, axis=1)

def exibir_graficos_analise(df):
    """Exibir gráficos de análise das cargas"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Frete por Saca vs Volume")
        
        fig1 = px.scatter(
            df, 
            x='Volume (sacas)', 
            y='Frete por Saca (R$)',
            size='Distância (km)',
            color='Transportadora',
            hover_data=['Vendedor', 'Origem', 'Destino', 'Status'],
            title='Relação Volume x Frete por Saca'
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("#### 🚚 Frete Médio por Transportadora")
        
        frete_por_transp = df.groupby('Transportadora')['Frete por Saca (R$)'].mean().reset_index()
        
        fig2 = px.bar(
            frete_por_transp, 
            x='Transportadora', 
            y='Frete por Saca (R$)',
            title='Frete Médio por Saca por Transportadora',
            color='Frete por Saca (R$)',
            color_continuous_scale='RdYlGn_r'
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

def exibir_insights_cargas(df):
    """Exibir insights e alertas sobre as cargas"""
    
    st.markdown("#### 💡 Insights e Alertas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Carga com maior frete por saca
        max_frete_idx = df['Frete por Saca (R$)'].idxmax()
        max_frete_carga = df.loc[max_frete_idx]
        
        st.error(f"""
        **🔴 MAIOR FRETE POR SACA**
        
        **Carga:** {max_frete_carga['ID']}  
        **Frete:** R$ {max_frete_carga['Frete por Saca (R$)']:.2f}/saca  
        **Vendedor:** {max_frete_carga['Vendedor']}  
        **Rota:** {max_frete_carga['Origem'][:20]}... → {max_frete_carga['Destino'][:15]}...  
        **Transportadora:** {max_frete_carga['Transportadora']}
        """)
    
    with col2:
        # Carga com menor frete por saca
        min_frete_idx = df['Frete por Saca (R$)'].idxmin()
        min_frete_carga = df.loc[min_frete_idx]
        
        st.success(f"""
        **🟢 MENOR FRETE POR SACA**
        
        **Carga:** {min_frete_carga['ID']}  
        **Frete:** R$ {min_frete_carga['Frete por Saca (R$)']:.2f}/saca  
        **Vendedor:** {min_frete_carga['Vendedor']}  
        **Rota:** {min_frete_carga['Origem'][:20]}... → {min_frete_carga['Destino'][:15]}...  
        **Transportadora:** {min_frete_carga['Transportadora']}
        """)
    
    with col3:
        # Análise de eficiência
        frete_medio = df['Frete por Saca (R$)'].mean()
        acima_media = len(df[df['Frete por Saca (R$)'] > frete_medio])
        
        st.warning(f"""
        **⚠️ ANÁLISE DE EFICIÊNCIA**
        
        **Frete Médio:** R$ {frete_medio:.2f}/saca  
        **Acima da Média:** {acima_media} cargas  
        **Abaixo da Média:** {len(df) - acima_media} cargas  
        **Economia Potencial:** R$ {(df['Frete por Saca (R$)'].max() - df['Frete por Saca (R$)'].min()) * df['Volume (sacas)'].mean():.0f}
        """)

def secao_gestao_cargas():
    """Seção principal de gestão de cargas"""
    
    st.markdown("# 🚛 Gestão de Cargas")
    st.markdown("### Controle completo de cargas com análise de frete por saca")
    
    # Carregar dados
    df_cargas = criar_dados_cargas()
    
    # Exibir métricas
    exibir_metricas_cargas(df_cargas)
    
    st.markdown("---")
    
    # Aplicar filtros
    st.markdown("### 🔍 Filtros")
    df_filtered = aplicar_filtros_cargas(df_cargas)
    
    st.markdown("---")
    
    # Tabela principal com destaque na coluna Frete por Saca
    st.markdown("### 📋 Tabela de Cargas")
    st.markdown("**Coluna 'Frete por Saca' destacada em amarelo**")
    
    # Exibir tabela com destaque
    styled_df = destacar_frete_por_saca(df_filtered)
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    st.markdown("---")
    
    # Gráficos de análise
    st.markdown("### 📊 Análises")
    exibir_graficos_analise(df_filtered)
    
    st.markdown("---")
    
    # Insights e alertas
    exibir_insights_cargas(df_filtered)
    
    # Resumo por transportadora
    st.markdown("---")
    st.markdown("### 📈 Resumo por Transportadora")
    
    resumo_transp = df_filtered.groupby('Transportadora').agg({
        'Frete por Saca (R$)': ['mean', 'min', 'max'],
        'Volume (sacas)': 'sum',
        'ID': 'count',
        'Frete Total (R$)': 'sum'
    }).round(2)
    
    resumo_transp.columns = [
        'Frete Médio/Saca', 'Frete Mín/Saca', 'Frete Máx/Saca',
        'Volume Total', 'Qtd Cargas', 'Frete Total'
    ]
    
    st.dataframe(resumo_transp, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="Gestão de Cargas - Fox SA",
        page_icon="🚛",
        layout="wide"
    )
    
    secao_gestao_cargas()

