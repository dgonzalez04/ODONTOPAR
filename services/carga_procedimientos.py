import pandas as pd
from db.connection import executemany


def cargar_excel(uploaded_file) -> dict:
    """
    Procesa el Excel maestro de procedimientos.

    Columnas esperadas: Código, Procedimiento, Garantía, Unidad
    Retorna un dict con contadores: insertados, actualizados, errores.
    """
    df = pd.read_excel(uploaded_file, dtype=str)
    df.columns = df.columns.str.strip()

    col_map = _detectar_columnas(df)
    if col_map is None:
        raise ValueError(
            "No se encontraron las columnas esperadas. "
            "El archivo debe tener: Código, Procedimiento, Garantía."
        )

    registros = []
    errores = []

    for idx, row in df.iterrows():
        codigo = str(row[col_map["codigo"]]).strip()
        descripcion = str(row[col_map["descripcion"]]).strip()
        validez_raw = row.get(col_map.get("garantia"))

        if not codigo or codigo.lower() == "nan":
            continue

        validez = _parse_validez(validez_raw)
        registros.append((codigo, descripcion, validez))

    if not registros:
        raise ValueError("El archivo no contiene registros válidos.")

    sql = """
        INSERT INTO procedimientos (codigo, descripcion, validez_dias)
        VALUES (%s, %s, %s)
        ON CONFLICT (codigo) DO UPDATE
            SET descripcion  = EXCLUDED.descripcion,
                validez_dias = EXCLUDED.validez_dias
    """
    executemany(sql, registros)

    return {"procesados": len(registros), "errores": errores}


def _detectar_columnas(df: pd.DataFrame) -> dict | None:
    """Mapea nombres de columnas del Excel a claves internas."""
    mapeos_posibles = {
        "codigo":     ["código", "codigo", "cod", "code"],
        "descripcion": ["procedimiento", "descripcion", "descripción", "nombre"],
        "garantia":   ["garantía", "garantia", "validez", "días", "dias"],
    }
    resultado = {}
    cols_lower = {c.lower(): c for c in df.columns}

    for clave, opciones in mapeos_posibles.items():
        for opcion in opciones:
            if opcion.lower() in cols_lower:
                resultado[clave] = cols_lower[opcion.lower()]
                break

    if "codigo" not in resultado or "descripcion" not in resultado:
        return None
    return resultado


def _parse_validez(valor) -> int | None:
    """Convierte el valor de garantía a entero o None."""
    if pd.isna(valor) or str(valor).strip().lower() in ("", "nan", "none", "null"):
        return None
    try:
        return int(float(str(valor).strip()))
    except (ValueError, TypeError):
        return None
