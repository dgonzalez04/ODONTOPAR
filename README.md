# ODONTOPAR — Sistema de Gestión Odontológica

Sistema web gratuito para gestión de atenciones, procedimientos y vencimientos de garantías.

## Stack

- **Frontend/Backend**: Python + Streamlit
- **Base de datos**: PostgreSQL en Supabase (free tier)
- **Deploy**: Streamlit Community Cloud (gratuito)

---

## Configuración inicial

### 1. Crear base de datos en Supabase

1. Crear cuenta en [supabase.com](https://supabase.com)
2. Crear un nuevo proyecto
3. Ir a **SQL Editor** y ejecutar el contenido de `db/schema.sql`
4. Copiar los datos de conexión: host, puerto, nombre, usuario y contraseña

### 2. Configurar credenciales localmente

```bash
cp .env.example .env
# Editar .env con los datos de Supabase
```

Crear `.streamlit/secrets.toml` (copiar de `.streamlit/secrets.toml.example`) y completar con:
- Datos de conexión a Supabase
- Usuario y contraseña de la app

Para generar el hash de contraseña:
```python
import bcrypt
print(bcrypt.hashpw(b"tu_contraseña", bcrypt.gensalt()).decode())
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar localmente

```bash
streamlit run app.py
```

---

## Deploy en Streamlit Community Cloud

1. Subir el proyecto a GitHub (sin `.env` ni `secrets.toml`)
2. Crear cuenta en [share.streamlit.io](https://share.streamlit.io)
3. Conectar el repositorio y seleccionar `app.py` como archivo principal
4. En **Advanced settings → Secrets**, pegar el contenido de `secrets.toml`

---

## Estructura del proyecto

```
ODONTOPAR/
├── app.py                          # Página principal con login
├── auth.py                         # Módulo de autenticación
├── pages/
│   ├── 01_Carga_Procedimientos.py  # Importar maestro de procedimientos
│   ├── 02_Carga_Atenciones.py      # Importar atenciones
│   ├── 03_Consulta_Pacientes.py    # Historial por paciente
│   └── 04_Reporte_Vencimientos.py  # Reporte de garantías vencidas
├── db/
│   ├── connection.py               # Conexión a PostgreSQL
│   └── schema.sql                  # DDL de tablas
├── services/
│   ├── carga_procedimientos.py     # Lógica de importación de procedimientos
│   ├── carga_atenciones.py         # Lógica de importación + regla ULTIMA/HISTORICO
│   └── vencimientos.py             # Cálculo de vencimientos e historial
├── requirements.txt
└── .env.example
```

---

## Formato de archivos Excel

### Maestro de Procedimientos
| Código | Procedimiento | Garantía | Unidad |
|--------|---------------|----------|--------|
| P001   | Amalgama      | 365      | días   |

### Atenciones
| Código Paciente | Nombre Paciente | Fecha Atención | Código Procedimiento | Descripción Procedimiento | Código Orden |
|-----------------|-----------------|----------------|---------------------|--------------------------|--------------|
| PAC001          | Juan Pérez      | 01/03/2024     | P001                | Amalgama                 | ORD-001      |
