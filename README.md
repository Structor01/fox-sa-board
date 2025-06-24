# 🌾 FOX SA - Board de Gestão

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.46+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Dashboard executivo completo para gestão financeira e operacional do Grupo FOX SA, especializado no agronegócio de grãos (Soja, Milho e Sorgo).

## 📊 Visão Geral

O **FOX SA Board de Gestão** é uma aplicação web interativa desenvolvida em Streamlit que oferece uma visão consolidada e detalhada das demonstrações financeiras e indicadores de performance das três empresas do grupo:

- **🌾 Fox Grãos** - Comercialização e logística de grãos
- **🚛 Fox Log** - Transporte de grãos e insumos do agronegócio  
- **💼 Clube FX** - Consultoria de comercialização agrícola

## ✨ Funcionalidades

### 📈 Dashboard Executivo
- **Visão Consolidada** do grupo com métricas principais
- **Análise Individual** por empresa
- **Performance por Commodity** (Soja, Milho, Sorgo)
- **Indicadores Financeiros** comparativos

### 📊 Demonstrações Financeiras
- **Balanço Patrimonial** completo
- **DRE** (Demonstração do Resultado do Exercício)
- **Indicadores de Liquidez, Endividamento e Rentabilidade**
- **Análise de Margens** e performance operacional

### 🎯 Indicadores Específicos por Segmento
- **Fox Grãos**: Volume comercializado, capacidade de armazenagem, margem por commodity
- **Fox Log**: Taxa de ocupação da frota, km rodados, custo operacional
- **Clube FX**: Receita por cliente, taxa de retenção, horas de consultoria

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/fox-sa-board.git
cd fox-sa-board
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**
```bash
streamlit run src/app.py
```

4. **Acesse no navegador**
```
http://localhost:8501
```

## 📁 Estrutura do Projeto

```
fox-sa-board/
├── src/
│   ├── app.py                 # Aplicação principal Streamlit
│   └── gerar_dados_fox.py     # Módulo de dados simulados
├── docs/
│   ├── documentacao_fox_board.md    # Manual completo
│   └── fox_board_esboco.md          # Documentação do projeto
├── assets/
│   └── screenshots/           # Capturas de tela da aplicação
├── requirements.txt           # Dependências Python
├── README.md                 # Este arquivo
└── LICENSE                   # Licença do projeto
```

## 🎨 Screenshots

### Dashboard Principal
![Dashboard Principal](assets/screenshots/dashboard-principal.png)

### Análise por Commodity
![Análise por Commodity](assets/screenshots/analise-commodity.png)

### Indicadores Financeiros
![Indicadores Financeiros](assets/screenshots/indicadores-financeiros.png)

## 🔧 Tecnologias Utilizadas

- **[Streamlit](https://streamlit.io/)** - Framework para aplicações web em Python
- **[Plotly](https://plotly.com/python/)** - Biblioteca para visualizações interativas
- **[Pandas](https://pandas.pydata.org/)** - Manipulação e análise de dados
- **[NumPy](https://numpy.org/)** - Computação científica

## 📊 Dados

O sistema utiliza dados simulados realistas para demonstração. A estrutura está preparada para fácil integração com banco de dados real:

### Integração com Banco de Dados
```python
# Exemplo de integração
def obter_dados_fox_graos():
    conn = sqlite3.connect('fox_database.db')
    balanco = pd.read_sql('SELECT * FROM balanco_fox_graos', conn)
    dre = pd.read_sql('SELECT * FROM dre_fox_graos', conn)
    return balanco, dre
```

## 🎯 Indicadores Implementados

### Financeiros
- **Liquidez Corrente**: AC / PC
- **Endividamento Total**: (PC + PNC) / Ativo Total
- **Margem Bruta**: Lucro Bruto / Receita Líquida
- **ROE**: Lucro Líquido / Patrimônio Líquido
- **ROA**: Lucro Líquido / Ativo Total

### Operacionais
- **Volume por Commodity**: Toneladas comercializadas/transportadas
- **Margem por Tonelada**: Spread de comercialização
- **Taxa de Ocupação**: Utilização da frota de transporte
- **Receita por Cliente**: Performance da consultoria

## 🔄 Roadmap

- [ ] Integração com banco de dados real
- [ ] Autenticação e controle de acesso
- [ ] Exportação de relatórios em PDF
- [ ] Dashboard mobile otimizado
- [ ] Alertas e notificações automáticas
- [ ] Análise preditiva com IA

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Contato

**FOX SA** - Grupo do Agronegócio

- 📧 Email: contato@foxsa.com.br
- 🌐 Website: [www.foxsa.com.br](https://www.foxsa.com.br)
- 📱 LinkedIn: [FOX SA](https://linkedin.com/company/foxsa)

---

<div align="center">
  <strong>Desenvolvido com ❤️ para o agronegócio brasileiro</strong>
</div>

