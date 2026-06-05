import streamlit as st
from auth import login_form
from services.carga_atenciones import cargar_excel

if not login_form():
    st.stop()

st.title("📥 Carga de Atenciones")
st.markdown(
    "Importá el archivo de atenciones desde Excel. "
    "El sistema aplicará automáticamente la regla **ULTIMA / HISTORICO** "
    "por cada combinación de paciente y procedimiento."
)

uploaded = st.file_uploader("Seleccioná el archivo Excel", type=["xlsx", "xls"])

if uploaded:
    if st.button("Procesar archivo"):
        with st.spinner("Procesando atenciones..."):
            try:
                resultado = cargar_excel(uploaded)
                st.success(f"✅ {resultado['insertados']} atenciones insertadas correctamente.")
                if resultado["errores"]:
                    with st.expander(f"⚠️ {len(resultado['errores'])} filas con error"):
                        for e in resultado["errores"]:
                            st.warning(e)
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Error inesperado: {e}")
