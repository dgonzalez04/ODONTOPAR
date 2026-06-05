import streamlit as st
from auth import login_form
from services.carga_procedimientos import cargar_excel
from db.connection import execute
import pandas as pd

if not login_form():
    st.stop()

st.title("📋 Carga de Procedimientos")
st.markdown(
    "Importá el maestro de procedimientos desde un archivo Excel. "
    "Si un procedimiento ya existe, se actualizará su descripción y garantía."
)

uploaded = st.file_uploader("Seleccioná el archivo Excel", type=["xlsx", "xls"])

if uploaded:
    if st.button("Procesar archivo"):
        with st.spinner("Procesando..."):
            try:
                resultado = cargar_excel(uploaded)
                st.success(f"✅ {resultado['procesados']} procedimientos procesados correctamente.")
                if resultado["errores"]:
                    with st.expander(f"⚠️ {len(resultado['errores'])} advertencias"):
                        for e in resultado["errores"]:
                            st.warning(e)
            except ValueError as e:
                st.error(str(e))

st.markdown("---")
st.subheader("Procedimientos registrados")

rows = execute("SELECT codigo, descripcion, validez_dias FROM procedimientos ORDER BY codigo", fetch=True)
if rows:
    df = pd.DataFrame([dict(r) for r in rows])
    df.columns = ["Código", "Descripción", "Garantía (días)"]
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No hay procedimientos cargados aún.")
