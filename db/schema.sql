-- Ejecutar este script en el SQL Editor de Supabase

CREATE TABLE IF NOT EXISTS pacientes (
    codigo  VARCHAR(50)  PRIMARY KEY,
    nombre  VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS procedimientos (
    codigo       VARCHAR(50)  PRIMARY KEY,
    descripcion  VARCHAR(255) NOT NULL,
    validez_dias INTEGER      -- NULL = no participa en análisis de vencimientos
);

CREATE TABLE IF NOT EXISTS atenciones (
    id                SERIAL       PRIMARY KEY,
    cod_paciente      VARCHAR(50)  NOT NULL REFERENCES pacientes(codigo),
    cod_procedimiento VARCHAR(50)  NOT NULL REFERENCES procedimientos(codigo),
    fecha_atencion    DATE         NOT NULL,
    cod_orden         VARCHAR(100),
    estado            VARCHAR(10)  NOT NULL CHECK (estado IN ('ULTIMA', 'HISTORICO')),
    fecha_carga       TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Garantiza que la búsqueda de la atención ULTIMA sea rápida
CREATE INDEX IF NOT EXISTS idx_atenciones_ultima
    ON atenciones(cod_paciente, cod_procedimiento)
    WHERE estado = 'ULTIMA';
