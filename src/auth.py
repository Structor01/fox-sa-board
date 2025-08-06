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
    """Tela de login ultra minimalista Steve Jobs"""
    
    # CSS ultra minimalista para login
    st.markdown("""
    <style>
    /* Login ultra minimalista */
    .login-ultra-minimal {
        max-width: 280px;
        margin: 0 auto;
        padding: 1rem 0;
        text-align: center;
    }
    
    /* Remover espaço superior */
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
    }
    
    .stApp > header {
        display: none !important;
    }
    
    .appview-container .main .block-container {
        padding-top: 0rem !important;
        max-width: 100% !important;
    }
    
    .login-title-minimal {
        font-size: 3rem;
        font-weight: 100;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .login-subtitle-minimal {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* Campos ultra minimalistas */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 4px !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Botão ultra minimalista */
    .stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        margin-top: 1rem !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.9) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Esconder labels */
    .stTextInput label {
        display: none !important;
    }
    
    /* Esconder elementos do form */
    .stForm {
        border: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container ultra minimalista
    st.markdown('<div class="login-ultra-minimal">', unsafe_allow_html=True)
    
    # Título ultra minimalista
    st.markdown('<h1 class="login-title-minimal">FOX SA</h1>', unsafe_allow_html=True)
    st.markdown('<p class="login-subtitle-minimal">Investment Board</p>', unsafe_allow_html=True)
    
    # Formulário ultra minimalista
    with st.form("login_minimal", clear_on_submit=False):
        username = st.text_input("", placeholder="Username", key="user_min")
        password = st.text_input("", placeholder="Password", type="password", key="pass_min")
        login_button = st.form_submit_button("Sign In")
    
    # Processar login
    if login_button:
        if username and password:
            user_data = authenticate_user(username, password)
            if user_data:
                st.session_state["authenticated"] = True
                st.session_state["user_data"] = user_data
                st.rerun()
            else:
                st.error("Invalid credentials")
        else:
            st.warning("Please fill all fields")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Credenciais discretas no canto
    st.markdown("""
    <div style="position: fixed; bottom: 15px; left: 15px; font-size: 0.65rem; color: rgba(255,255,255,0.25); line-height: 1.3;">
    admin/admin<br>gestor/gestor123
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

