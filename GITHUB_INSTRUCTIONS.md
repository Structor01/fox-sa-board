# 🚀 INSTRUÇÕES PARA SUBIR NO GITHUB

## 📋 Pré-requisitos
- Conta no GitHub criada
- Git configurado localmente (já feito)
- Repositório local pronto (já feito)

## 🔧 Passos para Subir no GitHub

### 1. Criar Repositório no GitHub
1. Acesse [github.com](https://github.com)
2. Clique em "New repository" (botão verde)
3. Configure o repositório:
   - **Repository name**: `fox-sa-board`
   - **Description**: `Dashboard executivo para gestão financeira do Grupo FOX SA - Agronegócio`
   - **Visibility**: Private ou Public (sua escolha)
   - **NÃO** marque "Add a README file" (já temos um)
   - **NÃO** marque "Add .gitignore" (já temos um)
   - **NÃO** marque "Choose a license" (já temos um)
4. Clique em "Create repository"

### 2. Conectar Repositório Local ao GitHub
No terminal, dentro da pasta `/home/ubuntu/fox-sa-board`, execute:

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/fox-sa-board.git

# Fazer o push inicial
git push -u origin main
```

### 3. Verificar Upload
1. Atualize a página do repositório no GitHub
2. Verifique se todos os arquivos foram enviados
3. Confirme se o README.md está sendo exibido corretamente

## 📁 Estrutura Enviada

```
fox-sa-board/
├── 📄 README.md                    # Documentação principal
├── 📄 LICENSE                      # Licença MIT
├── 📄 requirements.txt             # Dependências Python
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 📁 src/
│   ├── 🐍 app.py                   # Aplicação Streamlit principal
│   └── 🐍 gerar_dados_fox.py       # Módulo de dados simulados
├── 📁 docs/
│   ├── 📄 documentacao_fox_board.md # Manual completo
│   └── 📄 fox_board_esboco.md       # Documentação do projeto
├── 📁 assets/
│   └── 📁 screenshots/             # Pasta para capturas de tela
└── 📁 .streamlit/
    └── 📄 config.toml              # Configuração do Streamlit
```

## 🎯 Próximos Passos Após Upload

### 1. Adicionar Screenshots
```bash
# Adicionar imagens do dashboard
git add assets/screenshots/
git commit -m "📸 Add dashboard screenshots"
git push
```

### 2. Configurar GitHub Pages (Opcional)
- Para hospedar documentação estática
- Ir em Settings > Pages
- Selecionar source: Deploy from a branch
- Branch: main, folder: /docs

### 3. Adicionar Badges ao README
- Build status
- License badge
- Version badge
- Contributors

### 4. Configurar Issues e Projects
- Templates para bugs e features
- Milestones para versões
- Projects para roadmap

## 🔐 Autenticação

Se for solicitado usuário/senha durante o push:
- **Username**: Seu username do GitHub
- **Password**: Personal Access Token (não a senha da conta)

### Como criar Personal Access Token:
1. GitHub > Settings > Developer settings
2. Personal access tokens > Tokens (classic)
3. Generate new token
4. Selecionar scopes: `repo` (full control)
5. Copiar o token gerado

## ✅ Verificação Final

Após o push, confirme:
- [ ] Todos os arquivos foram enviados
- [ ] README.md está sendo exibido
- [ ] Estrutura de pastas está correta
- [ ] Badges estão funcionando
- [ ] Links no README estão corretos

## 🆘 Problemas Comuns

### Erro de autenticação:
```bash
git config --global credential.helper store
```

### Erro de branch:
```bash
git branch -M main
git push -u origin main
```

### Repositório já existe:
```bash
git remote set-url origin https://github.com/SEU_USUARIO/fox-sa-board.git
```

---

**🎉 Parabéns! Seu repositório estará no GitHub e pronto para colaboração!**

