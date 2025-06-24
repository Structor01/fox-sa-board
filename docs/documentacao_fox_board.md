# 📋 DOCUMENTAÇÃO - BOARD DE GESTÃO FOX SA

## 🎯 VISÃO GERAL

O Board de Gestão FOX SA é uma aplicação web interativa desenvolvida em Streamlit que oferece uma visão completa e integrada das demonstrações financeiras e indicadores de performance das três empresas do grupo:

- **🌾 Fox Grãos**: Comercialização e logística de grãos (Soja, Milho, Sorgo)
- **🚛 Fox Log**: Transporte de grãos e insumos do agronegócio
- **💼 Clube FX**: Consultoria de comercialização agrícola

## 🚀 ACESSO À APLICAÇÃO

**URL de Acesso**: https://8501-i8y5xfln0c06b75txdf8u-287da109.manusvm.computer

A aplicação está rodando em servidor temporário para demonstração. Para uso em produção, recomenda-se deploy em servidor próprio.

## 📊 FUNCIONALIDADES PRINCIPAIS

### 1. 🏠 VISÃO CONSOLIDADA
- **Métricas Principais**: Receita líquida, EBITDA, Lucro líquido, Margem EBITDA
- **Gráficos Comparativos**: Receita por empresa e volume por commodity
- **Demonstrações Consolidadas**: Balanço Patrimonial e DRE do grupo

### 2. 🌾 FOX GRÃOS
- **Indicadores Operacionais**: Volume total, capacidade de armazenagem
- **Performance por Commodity**: Dados detalhados de Soja, Milho e Sorgo
- **Demonstrações Financeiras**: Balanço e DRE específicos

### 3. 🚛 FOX LOG
- **Métricas de Frota**: Total de veículos, km rodados, taxa de ocupação
- **Transporte por Commodity**: Volume e receita por tipo de grão
- **Demonstrações Financeiras**: Balanço e DRE específicos

### 4. 💼 CLUBE FX
- **Indicadores de Consultoria**: Clientes ativos, receita por cliente, taxa de retenção
- **Assessoria por Commodity**: Volume assessorado e comissões
- **Demonstrações Financeiras**: Balanço e DRE específicos

### 5. 📊 ANÁLISE POR COMMODITY
- **Comparativo de Volumes**: Dados consolidados por grão
- **Análise de Margens**: Performance financeira por commodity
- **Análise de Preços**: Spreads e margens de comercialização

### 6. 📈 INDICADORES COMPARATIVOS
- **Indicadores Financeiros**: Liquidez, endividamento, rentabilidade
- **Gráficos Comparativos**: Margens, liquidez e endividamento por empresa
- **Análise Consolidada**: Performance do grupo vs. empresas individuais

## 🔧 ESTRUTURA TÉCNICA

### Arquivos Principais:
- `fox_board_streamlit.py`: Aplicação principal Streamlit
- `gerar_dados_fox.py`: Módulo de geração de dados simulados
- `fox_board_esboco.md`: Documentação do projeto
- `todo.md`: Controle de progresso do desenvolvimento

### Tecnologias Utilizadas:
- **Frontend**: Streamlit
- **Visualização**: Plotly
- **Dados**: Pandas, NumPy
- **Backend**: Python 3.11

## 📈 INDICADORES IMPLEMENTADOS

### Indicadores de Liquidez:
- **Liquidez Corrente**: Ativo Circulante / Passivo Circulante
- **Liquidez Seca**: (AC - Estoques) / Passivo Circulante
- **Liquidez Geral**: (AC + RLP) / (PC + PNC)

### Indicadores de Endividamento:
- **Endividamento Total**: (PC + PNC) / Ativo Total
- **Endividamento de Curto Prazo**: PC / Ativo Total
- **Composição do Endividamento**: PC / (PC + PNC)

### Indicadores de Rentabilidade:
- **Margem Bruta**: Lucro Bruto / Receita Líquida
- **Margem EBITDA**: EBITDA / Receita Líquida
- **Margem Líquida**: Lucro Líquido / Receita Líquida
- **ROE**: Lucro Líquido / Patrimônio Líquido
- **ROA**: Lucro Líquido / Ativo Total

### Indicadores Específicos por Segmento:
- **Fox Grãos**: Volume por commodity, margem por tonelada, capacidade de armazenagem
- **Fox Log**: Taxa de ocupação da frota, km rodados, custo operacional
- **Clube FX**: Receita por cliente, taxa de retenção, horas de consultoria

## 🔄 INTEGRAÇÃO COM BANCO DE DADOS

### Estrutura Preparada para Integração:
O sistema foi desenvolvido com dados simulados, mas está estruturado para fácil integração com banco de dados real:

1. **Substituir Dados Simulados**: Modificar as funções em `gerar_dados_fox.py`
2. **Conectar Base de Dados**: Implementar conexões SQL/NoSQL
3. **Atualização em Tempo Real**: Configurar refresh automático dos dados
4. **Histórico**: Implementar armazenamento de dados históricos

### Exemplo de Integração:
```python
# Substituir função de dados simulados
def obter_dados_fox_graos():
    # Conectar ao banco de dados
    conn = sqlite3.connect('fox_database.db')
    
    # Consultar dados reais
    balanco = pd.read_sql('SELECT * FROM balanco_fox_graos', conn)
    dre = pd.read_sql('SELECT * FROM dre_fox_graos', conn)
    
    return balanco, dre
```

## 🎨 PERSONALIZAÇÃO

### Cores e Tema:
- **Cor Principal**: Verde (#2E8B57) - representa o agronegócio
- **Cores Secundárias**: Tons de verde para harmonia visual
- **Commodities**: Cores específicas (Soja: marrom, Milho: dourado, Sorgo: bege)

### Layout Responsivo:
- **Desktop**: Layout em colunas para máximo aproveitamento
- **Mobile**: Adaptação automática para dispositivos móveis
- **Tablets**: Interface otimizada para telas médias

## 📱 NAVEGAÇÃO

### Menu Lateral:
- **🏠 Visão Consolidada**: Dashboard principal do grupo
- **🌾 Fox Grãos**: Dados específicos da comercializadora
- **🚛 Fox Log**: Informações da transportadora
- **💼 Clube FX**: Métricas da consultoria
- **📊 Análise por Commodity**: Comparativo por grão
- **📈 Indicadores Comparativos**: Análise financeira consolidada

## 🔧 MANUTENÇÃO E SUPORTE

### Atualizações:
- **Dados**: Atualização manual ou automática via integração
- **Funcionalidades**: Adição de novos indicadores e visualizações
- **Performance**: Otimização de consultas e carregamento

### Backup:
- **Código**: Versionamento em Git
- **Dados**: Backup regular da base de dados
- **Configurações**: Documentação de configurações customizadas

## 📞 PRÓXIMOS PASSOS

1. **Teste da Aplicação**: Validar todas as funcionalidades
2. **Integração de Dados**: Conectar com banco de dados real
3. **Deploy Produção**: Configurar servidor definitivo
4. **Treinamento**: Capacitar usuários finais
5. **Monitoramento**: Implementar logs e métricas de uso

---

**Desenvolvido para FOX SA** | Versão 1.0 | Data: Dezembro 2024

