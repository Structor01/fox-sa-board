import streamlit as st
import hashlib
import hmac
from typing import Dict, Optional

# Configuração de usuários (em produção, usar banco de dados)
USERS_DB = {
    "admin": {
        "password_hash": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # admin
        "name": "Administrador",
        "role": "admin"
    },
    "fox.admin": {
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # fox2024
        "name": "FOX Admin",
        "role": "admin"
    },
    "gestor": {
        "password_hash": "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5",  # gestor123
        "name": "Gestor",
        "role": "manager"
    },
    "viewer": {
        "password_hash": "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f",  # viewer123
        "name": "Visualizador",
        "role": "viewer"
    }
}

def hash_password(password: str) -> str:
    """Gera hash SHA256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return hmac.compare_digest(hash_password(password), password_hash)

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Autentica usuário e retorna dados se válido"""
    if username in USERS_DB:
        user_data = USERS_DB[username]
        if verify_password(password, user_data["password_hash"]):
            return {
                "username": username,
                "name": user_data["name"],
                "role": user_data["role"]
            }
    return None

def check_authentication() -> bool:
    """Verifica se o usuário está autenticado"""
    return st.session_state.get("authenticated", False)

def get_current_user() -> Optional[Dict]:
    """Retorna dados do usuário atual"""
    if check_authentication():
        return st.session_state.get("user_data")
    return None

def logout():
    """Faz logout do usuário"""
    for key in ["authenticated", "user_data"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def show_login_page():
    """Exibe a página de login minimalista Steve Jobs"""
    
    # Container principal minimalista
    st.markdown('<div class="login-container-jobs">', unsafe_allow_html=True)
    
    # Header minimalista
    st.markdown('<h1 class="login-header-jobs">FOX SA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.9rem; font-weight: 300; margin-bottom: 3rem;">Investment Board</p>', unsafe_allow_html=True)
    
    # Credenciais simples
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid rgba(255,255,255,0.1);">
        <div style="color: rgba(255,255,255,0.8); font-weight: 400; margin-bottom: 1rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Demo Access</div>
        <div style="font-size: 0.85rem; line-height: 1.6;">
            <div style="color: #ffffff; margin-bottom: 0.5rem;"><strong>admin</strong> / admin</div>
            <div style="color: #ffffff; margin-bottom: 0.5rem;"><strong>fox.admin</strong> / fox2024</div>
            <div style="color: #ffffff; margin-bottom: 0.5rem;"><strong>gestor</strong> / gestor123</div>
            <div style="color: #ffffff;"><strong>viewer</strong> / viewer123</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário minimalista
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button("Sign In", use_container_width=True)
    
    # Processar login
    if login_button:
        if username and password:
            user_data = authenticate_user(username, password)
            if user_data:
                st.session_state["authenticated"] = True
                st.session_state["user_data"] = user_data
                st.success(f"Welcome, {user_data['name']}")
                st.rerun()
            else:
                st.error("Invalid credentials")
        else:
            st.warning("Please fill all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rodapé minimalista
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-top: 3rem; font-weight: 300;">
        Secure Authentication System
    </div>
    """, unsafe_allow_html=True)

def show_user_info():
    """Exibe informações do usuário logado na sidebar"""
    user = get_current_user()
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Usuário Logado")
        st.sidebar.write(f"**Nome:** {user['name']}")
        st.sidebar.write(f"**Usuário:** {user['username']}")
        st.sidebar.write(f"**Perfil:** {user['role'].title()}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()

def require_authentication(func):
    """Decorator para proteger funções que requerem autenticação"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            show_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper

# Função para adicionar novos usuários (apenas para admins)
def add_user(username: str, password: str, name: str, role: str = "viewer") -> bool:
    """Adiciona novo usuário (função para futuras implementações)"""
    if username not in USERS_DB:
        USERS_DB[username] = {
            "password_hash": hash_password(password),
            "name": name,
            "role": role
        }
        return True
    return False

def check_permission(required_role: str) -> bool:
    """Verifica se o usuário tem permissão para acessar determinada funcionalidade"""
    user = get_current_user()
    if not user:
        return False
    
    role_hierarchy = {
        "viewer": 1,
        "manager": 2,
        "admin": 3
    }
    
    user_level = role_hierarchy.get(user["role"], 0)
    required_level = role_hierarchy.get(required_role, 3)
    
    return user_level >= required_level

