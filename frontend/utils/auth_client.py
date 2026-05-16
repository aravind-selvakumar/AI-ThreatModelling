import streamlit as st

from utils.api_client import get_me, guest_login, login as api_login


def authenticate():
    if "token" in st.session_state and st.session_state.token:
        user = get_me(st.session_state.token)
        if user:
            return st.session_state.token, user.get("role", "guest"), user.get("username", "guest")
        st.session_state.token = None

    st.set_page_config(page_title="ThreatModellingEngine", page_icon="🛡️", layout="wide")

    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px; margin: 80px auto; text-align: center;
        }
        .login-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
        .login-subtitle { color: #666; margin-bottom: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🛡️ ThreatModellingEngine</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">AI-Powered STRIDE & DREAD Threat Analysis</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Admin Login", "Guest Access"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please enter username and password")
                else:
                    result = api_login(username, password)
                    if result:
                        st.session_state.token = result["access_token"]
                        st.session_state.role = result["role"]
                        st.session_state.username = result["username"]
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue as Guest", use_container_width=True, type="primary"):
            result = guest_login()
            if result:
                st.session_state.token = result["access_token"]
                st.session_state.role = "guest"
                st.session_state.username = "guest"
                st.rerun()
            else:
                st.error("Could not create guest session. Is the server running?")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
