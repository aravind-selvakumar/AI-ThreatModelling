import streamlit as st

st.set_page_config(page_title="ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" in st.session_state and st.session_state.token:
    st.switch_page("pages/1_Dashboard.py")

st.markdown(
    """
    <style>
    .login-container { max-width: 420px; margin: 100px auto; text-align: center; }
    .login-title { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.25rem; }
    .login-subtitle { color: #888; margin-bottom: 2rem; font-size: 0.95rem; }
    .stForm { border: 1px solid #333; padding: 1.5rem; border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<div class="login-title">🛡️ ThreatModellingEngine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="login-subtitle">AI-Powered STRIDE Threat Classification & DREAD Risk Scoring<br>'
    'with Retrieval-Augmented Generation (RAG)</div>',
    unsafe_allow_html=True,
)

from utils.api_client import guest_login, health_check, login as api_login

if not health_check():
    st.warning("⚠️ Backend server is not reachable. Make sure the API is running.")

tab1, tab2 = st.tabs(["🔐 Admin Login", "👤 Guest Access"])

with tab1:
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                result = api_login(username, password)
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.role = result["role"]
                    st.session_state.username = result["username"]
                    st.rerun()
                else:
                    st.error("Invalid username or password")

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("Access the tool without an account. Your models will be saved to this session.")
    if st.button("🚀 Continue as Guest", use_container_width=True, type="primary"):
        result = guest_login()
        if result:
            st.session_state.token = result["access_token"]
            st.session_state.role = "guest"
            st.session_state.username = "guest"
            st.rerun()
        else:
            st.error("Could not connect to the server. Please try again later.")

st.markdown("---")
st.caption("v0.1.0 • Secure-By-Design")
st.markdown("</div>", unsafe_allow_html=True)
