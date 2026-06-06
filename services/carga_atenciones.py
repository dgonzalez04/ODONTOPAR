import pandas as pd
from datetime import date
from db.connection import get_connection


def cargar_excel(uploaded_file) -> dict:
    """
    Procesa el Excel de atenciones.

    Columnas esperadas:
      Código paciente, Nombre paciente, Fecha atención,
      Código procedimiento, Descripción procedimiento, Código orden

    Aplica la regla ULTIMA/HISTORICO por cada par (paciente, procedimiento).
    Retorna contadores de la carga.
    """
    df = pd.read_excel(uploaded_file, dtype=str)
    df.columns = df.columns.str.strip()

    col_map = _detectar_columnas(df)
    if col_map is None:
        raise ValueError(
            "Columnas no reconocidas. Se esperan: "
            "Código paciente, Nombre paciente, Fecha atención, "
            "Código procedimiento, Descripción procedimiento, Código orden."
        )

    insertados = 0
    errores = []

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for idx, row in df.iterrows():
                    cod_pac   = str(row[col_map["cod_paciente"]]).strip()
                    nom_pac   = str(row[col_map["nom_paciente"]]).strip()
                    cod_proc  = str(row[col_map["cod_procedimiento"]]).strip()
                    desc_proc = str(row[col_map["desc_procedimiento"]]).strip()
                    cod_orden = str(row.get(col_map.get("cod_orden", ""), "")).strip()
                    fecha_raw = row[col_map["fecha_atencion"]]

                    if not cod_pac or cod_pac.lower() == "nan":
                        continue
                    if not cod_proc or cod_proc.lower() == "nan":
                        continue

                    fecha = _parse_fecha(fecha_raw)
                    if fecha is None:
                        errores.append(f"Fila {idx+2}: fecha inválida '{fecha_raw}'")
                        continue

                    # Auto-crear paciente si no existe
                    cur.execute(
                        """
                        INSERT INTO pacientes (codigo, nombre)
                        VALUES (%s, %s)
                        ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre
                        """,
                        (cod_pac, nom_pac),
                    )

                    # Auto-crear procedimiento si no existe (validez NULL)
                    cur.execute(
                        """
                        INSERT INTO procedimientos (codigo, descripcion, validez_dias)
                        VALUES (%s, %s, NULL)
                        ON CONFLICT (codigo) DO NOTHING
                        """,
                        (cod_proc, desc_proc),
                    )

                    # Marcar atención ULTIMA anterior como HISTORICO
                    cur.execute(
                        """
                        UPDATE atenciones
                        SET estado = 'HISTORICO'
                        WHERE cod_paciente = %s
                          AND cod_procedimiento = %s
                          AND estado = 'ULTIMA'
                        """,
                        (cod_pac, cod_proc),
                    )

                    # Insertar nueva atención como ULTIMA
                    cur.execute(
                        """
                        INSERT INTO atenciones
                            (cod_paciente, cod_procedimiento, fecha_atencion, cod_orden, estado)
                        VALUES (%s, %s, %s, %s, 'ULTIMA')
                        """,
                        (cod_pac, cod_proc, fecha, cod_orden or None),
                    )
                    insertados += 1
    finally:
        conn.close()

    return {"insertados": insertados, "errores": errores}


def _detectar_columnas(df: pd.DataFrame) -> dict | None:
    mapeos = {
        "cod_paciente":       ["código paciente", "codigo paciente", "cod paciente", "cod_paciente", "paciente"],
        "nom_paciente":       ["nombre paciente", "nombre", "nom_paciente", "nom paciente"],
        "fecha_atencion":     ["fecha atención", "fecha atencion", "fecha_atencion", "fecha"],
        "cod_procedimiento":  ["código procedimiento", "codigo procedimiento", "cod procedimiento", "cod_procedimiento"],
        "desc_procedimiento": ["descripción procedimiento", "descripcion procedimiento", "descripción", "descripcion", "procedimiento"],
        "cod_orden":          ["código orden", "codigo orden", "cod orden", "cod_orden", "orden"],
    }
    cols_lower = {c.lower(): c for c in df.columns}
    resultado = {}

    for clave, opciones in mapeos.items():
        for opcion in opciones:
            if opcion.lower() in cols_lower:
                resultado[clave] = cols_lower[opcion.lower()]
                break

    obligatorias = {"cod_paciente", "nom_paciente", "fecha_atencion", "cod_procedimiento"}
    if not obligatorias.issubset(resultado.keys()):
        return None
    return resultado


def _parse_fecha(valor) -> date | None:
    if pd.isna(valor):
        return None
    if isinstance(valor, date):
        return valor
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return pd.to_datetime(str(valor).strip(), format=fmt).date()
        except (ValueError, TypeError):
            continue
    try:
        return pd.to_datetime(str(valor).strip(), dayfirst=True).date()
    except Exception:
        return None
