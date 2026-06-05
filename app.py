import streamlit as st
from auth import login_form, logout

st.set_page_config(
    page_title="ODONTOPAR",
    page_icon="🦷",
    layout="wide",
)

if not login_form():
    st.stop()

# Barra lateral con navegación y botón de salida
with st.sidebar:
    st.title("🦷 ODONTOPAR")
    st.markdown("---")
    st.page_link("pages/01_Carga_Procedimientos.py", label="📋 Carga de Procedimientos")
    st.page_link("pages/02_Carga_Atenciones.py",    label="📥 Carga de Atenciones")
    st.page_link("pages/03_Consulta_Pacientes.py",  label="🔍 Consulta de Pacientes")
    st.page_link("pages/04_Reporte_Vencimientos.py",label="⚠️  Reporte de Vencimientos")
    st.markdown("---")
    if st.button("Cerrar sesión"):
        logout()

st.title("🦷 Sistema de Gestión Odontológica")
st.markdown(
    """
    Bienvenido al sistema **ODONTOPAR**.

    Utilizá el menú de la izquierda para navegar entre los módulos:

    | Módulo | Descripción |
    |---|---|
    | 📋 Carga de Procedimientos | Importar el maestro de procedimientos desde Excel |
    | 📥 Carga de Atenciones | Importar atenciones desde Excel |
    | 🔍 Consulta de Pacientes | Ver historial de atenciones por paciente |
    | ⚠️ Reporte de Vencimientos | Detectar garantías vencidas a una fecha |
    """
)
