import pandas as pd
from datetime import date
from db.connection import execute


def obtener_reporte(fecha_referencia: date) -> pd.DataFrame:
    """
    Calcula vencimientos de garantías a una fecha de referencia.

    Solo considera:
      - Atenciones con estado ULTIMA
      - Procedimientos con validez_dias IS NOT NULL

    Retorna un DataFrame con columnas:
      cod_paciente, nombre_paciente, cod_procedimiento, descripcion,
      fecha_atencion, dias_transcurridos, validez_dias, estado_vencimiento
    """
    sql = """
        SELECT
            p.codigo          AS cod_paciente,
            p.nombre          AS nombre_paciente,
            pr.codigo         AS cod_procedimiento,
            pr.descripcion    AS descripcion,
            a.fecha_atencion,
            pr.validez_dias,
            (%s::date - a.fecha_atencion) AS dias_transcurridos
        FROM atenciones a
        JOIN pacientes     p  ON p.codigo  = a.cod_paciente
        JOIN procedimientos pr ON pr.codigo = a.cod_procedimiento
        WHERE a.estado = 'ULTIMA'
          AND pr.validez_dias IS NOT NULL
        ORDER BY p.nombre, pr.descripcion
    """
    rows = execute(sql, (fecha_referencia,), fetch=True)

    if not rows:
        return pd.DataFrame(columns=[
            "cod_paciente", "nombre_paciente", "cod_procedimiento",
            "descripcion", "fecha_atencion", "dias_transcurridos",
            "validez_dias", "estado_vencimiento",
        ])

    df = pd.DataFrame([dict(r) for r in rows])
    df["estado_vencimiento"] = df.apply(
        lambda r: "VENCIDO" if r["dias_transcurridos"] > r["validez_dias"] else "VIGENTE",
        axis=1,
    )
    df["fecha_atencion"] = pd.to_datetime(df["fecha_atencion"]).dt.strftime("%d/%m/%Y")
    return df


def obtener_historial_paciente(cod_paciente: str) -> pd.DataFrame:
    """Retorna todas las atenciones (ULTIMA e HISTORICO) de un paciente."""
    sql = """
        SELECT
            pr.codigo       AS cod_procedimiento,
            pr.descripcion,
            a.fecha_atencion,
            a.cod_orden,
            a.estado,
            pr.validez_dias,
            a.fecha_carga
        FROM atenciones a
        JOIN procedimientos pr ON pr.codigo = a.cod_procedimiento
        WHERE a.cod_paciente = %s
        ORDER BY pr.descripcion, a.fecha_atencion DESC
    """
    rows = execute(sql, (cod_paciente,), fetch=True)
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    df["fecha_atencion"] = pd.to_datetime(df["fecha_atencion"]).dt.strftime("%d/%m/%Y")
    df["fecha_carga"] = pd.to_datetime(df["fecha_carga"]).dt.strftime("%d/%m/%Y %H:%M")
    return df
