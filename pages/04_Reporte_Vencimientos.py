import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
from auth import login_form
from services.vencimientos import obtener_reporte

if not login_form():
    st.stop()

st.title("⚠️ Reporte de Vencimientos")
st.markdown(
    "Seleccioná una fecha de referencia para detectar garantías vencidas. "
    "Solo se analizan atenciones **ULTIMA** de procedimientos con tiempo de garantía definido."
)

fecha_ref = st.date_input("Fecha de referencia", value=date.today())

filtro_estado = st.radio(
    "Mostrar",
    ["Todos", "Solo VENCIDOS", "Solo VIGENTES"],
    horizontal=True,
)

if st.button("Generar reporte"):
    with st.spinner("Calculando..."):
        df = obtener_reporte(fecha_ref)

    if df.empty:
        st.info("No hay atenciones con garantías definidas para analizar.")
    else:
        if filtro_estado == "Solo VENCIDOS":
            df = df[df["estado_vencimiento"] == "VENCIDO"]
        elif filtro_estado == "Solo VIGENTES":
            df = df[df["estado_vencimiento"] == "VIGENTE"]

        vencidos = len(df[df["estado_vencimiento"] == "VENCIDO"])
        vigentes = len(df[df["estado_vencimiento"] == "VIGENTE"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total analizados", len(df))
        col2.metric("🔴 Vencidos", vencidos)
        col3.metric("🟢 Vigentes", vigentes)

        st.markdown("---")

        # Color de filas según estado
        def _colorear(row):
            color = "#ffe0e0" if row["estado_vencimiento"] == "VENCIDO" else "#e0ffe0"
            return [f"background-color: {color}"] * len(row)

        df_display = df.rename(columns={
            "cod_paciente":       "Cód. Paciente",
            "nombre_paciente":    "Nombre Paciente",
            "cod_procedimiento":  "Cód. Procedimiento",
            "descripcion":        "Descripción",
            "fecha_atencion":     "Fecha Atención",
            "dias_transcurridos": "Días Transcurridos",
            "validez_dias":       "Garantía (días)",
            "estado_vencimiento": "Estado",
        })

        st.dataframe(
            df_display.style.apply(_colorear, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        # Exportar a Excel
        excel_bytes = _to_excel(df_display)
        st.download_button(
            label="📥 Descargar reporte (.xlsx)",
            data=excel_bytes,
            file_name=f"vencimientos_{fecha_ref.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _to_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Vencimientos")
        ws = writer.sheets["Vencimientos"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col) + 2
            ws.column_dimensions[col[0].column_letter].width = min(max_len, 50)
    return buf.getvalue()
