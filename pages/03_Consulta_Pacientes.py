import streamlit as st
from auth import login_form
from db.connection import execute
from services.vencimientos import obtener_historial_paciente

if not login_form():
    st.stop()

st.title("🔍 Consulta de Pacientes")

rows = execute("SELECT codigo, nombre FROM pacientes ORDER BY nombre", fetch=True)
if not rows:
    st.info("No hay pacientes registrados.")
    st.stop()

opciones = {f"{r['nombre']} ({r['codigo']})": r["codigo"] for r in rows}
seleccion = st.selectbox("Seleccioná un paciente", list(opciones.keys()))
cod = opciones[seleccion]

df = obtener_historial_paciente(cod)

if df.empty:
    st.info("Este paciente no tiene atenciones registradas.")
else:
    col1, col2 = st.columns(2)
    total = len(df)
    ultimas = len(df[df["estado"] == "ULTIMA"])
    col1.metric("Total atenciones", total)
    col2.metric("Procedimientos activos (ULTIMA)", ultimas)

    st.markdown("---")

    tab1, tab2 = st.tabs(["Atenciones ULTIMA", "Historial completo"])

    with tab1:
        df_ultima = df[df["estado"] == "ULTIMA"].drop(columns=["estado", "fecha_carga"])
        df_ultima.columns = ["Cód. Procedimiento", "Descripción", "Fecha Atención", "Cód. Orden", "Garantía (días)"]
        st.dataframe(df_ultima, use_container_width=True, hide_index=True)

    with tab2:
        df_hist = df.copy()
        df_hist.columns = ["Cód. Procedimiento", "Descripción", "Fecha Atención", "Cód. Orden", "Estado", "Garantía (días)", "Fecha Carga"]
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
