import bcrypt
import streamlit as st


def _check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def login_form() -> bool:
    """
    Muestra el formulario de login.
    Retorna True si el usuario está autenticado.
    """
    if st.session_state.get("autenticado"):
        return True

    st.title("🦷 ODONTOPAR")
    st.subheader("Iniciar sesión")

    with st.form("login"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Ingresar")

    if enviado:
        try:
            cfg = st.secrets["auth"]
            usuario_ok = usuario == cfg["username"]
            clave_ok = _check_password(clave, cfg["password_hash"])
        except KeyError:
            st.error("Configuración de autenticación no encontrada en secrets.toml.")
            return False

        if usuario_ok and clave_ok:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    return False


def logout():
    st.session_state["autenticado"] = False
    st.rerun()
