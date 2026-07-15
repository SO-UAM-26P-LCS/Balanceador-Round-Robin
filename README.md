# Balanceador de Carga Round Robin

API REST que simula un balanceador de carga usando el algoritmo Round Robin, desarrollada con FastAPI para la materia de Sistemas Operativos.

---

## Requisitos

- Python 3.8 o superior
- pip

---

## Instalación

### 1. Estructura del proyecto

```
balanceador-round-robin/
├── main.py
└── requirements.txt
```

### 2. Crear el entorno virtual

```bash
python3 -m venv .venv
```

### 3. Activar el entorno virtual

**En macOS / Linux:**
```bash
source .venv/bin/activate
```

**En Windows:**
```bash
.venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene:
```
fastapi
uvicorn
```

---

## Ejecución

```bash
uvicorn main:app --reload
```

La API quedará disponible en:
```
http://localhost:8000
```

La documentación interactiva generada automáticamente por FastAPI estará en:
```
http://localhost:8000/docs
```

---

## Servidores simulados

El sistema inicia con 5 servidores, todos activos y con contador en cero:

```json
[
  { "id": 1, "name": "Servidor 1", "active": true, "requests": 0 },
  { "id": 2, "name": "Servidor 2", "active": true, "requests": 0 },
  { "id": 3, "name": "Servidor 3", "active": true, "requests": 0 },
  { "id": 4, "name": "Servidor 4", "active": true, "requests": 0 },
  { "id": 5, "name": "Servidor 5", "active": true, "requests": 0 }
]
```

---

## Endpoints disponibles

### GET `/servers`
Devuelve la lista completa de los 5 servidores con su estado y contador de peticiones.

**Respuesta de ejemplo:**
```json
[
  { "id": 1, "name": "Servidor 1", "active": true, "requests": 2 },
  { "id": 2, "name": "Servidor 2", "active": true, "requests": 2 },
  { "id": 3, "name": "Servidor 3", "active": true, "requests": 1 },
  { "id": 4, "name": "Servidor 4", "active": true, "requests": 1 },
  { "id": 5, "name": "Servidor 5", "active": true, "requests": 1 }
]
```

---

### POST `/request`
Envía una petición al balanceador. El sistema asigna automáticamente el siguiente servidor activo siguiendo Round Robin e incrementa su contador.

**Cuerpo de la petición:**
```json
{
  "id": 1,
  "description": "Solicitud de prueba"
}
```

**Respuesta de ejemplo:**
```json
{
  "request_id": 1,
  "description": "Solicitud de prueba",
  "assigned_server": "Servidor 1",
  "server_id": 1
}
```

**Error si todos los servidores están caídos:**
```json
{ "detail": "No hay servidores disponibles" }
```
Código HTTP: `503 Service Unavailable`

---

### POST `/servers/{server_id}/down`
Desactiva un servidor. Deja de recibir peticiones hasta que se reactive.

**Ejemplo:**
```
POST /servers/2/down
```

**Respuesta:**
```json
{ "message": "Servidor 2 desactivado" }
```

**Error si el servidor no existe:**
```json
{ "detail": "Servidor no encontrado" }
```
Código HTTP: `404 Not Found`

---

### POST `/servers/{server_id}/up`
Reactiva un servidor desactivado. Vuelve a participar en la rotación Round Robin.

**Ejemplo:**
```
POST /servers/2/up
```

**Respuesta:**
```json
{ "message": "Servidor 2 activado" }
```

**Error si el servidor no existe:**
```json
{ "detail": "Servidor no encontrado" }
```
Código HTTP: `404 Not Found`

---

### POST `/servers/reset`
Reinicia el contador de peticiones de todos los servidores a cero.

**Respuesta:**
```json
{ "message": "Contadores de peticiones reiniciados" }
```

---

### GET `/servers/active`
Devuelve únicamente los servidores cuyo campo `active` es `true`.

**Respuesta de ejemplo (con Servidor 2 caído):**
```json
[
  { "id": 1, "name": "Servidor 1", "active": true, "requests": 3 },
  { "id": 3, "name": "Servidor 3", "active": true, "requests": 2 },
  { "id": 4, "name": "Servidor 4", "active": true, "requests": 2 },
  { "id": 5, "name": "Servidor 5", "active": true, "requests": 2 }
]
```

---

## Pruebas sugeridas

### 1. Consultar todos los servidores
```
GET /servers
```

### 2. Enviar varias peticiones y observar la rotación circular
```
POST /request  →  body: { "id": 1, "description": "prueba" }  →  Servidor 1
POST /request  →  body: { "id": 2, "description": "prueba" }  →  Servidor 2
POST /request  →  body: { "id": 3, "description": "prueba" }  →  Servidor 3
POST /request  →  body: { "id": 4, "description": "prueba" }  →  Servidor 4
POST /request  →  body: { "id": 5, "description": "prueba" }  →  Servidor 5
POST /request  →  body: { "id": 6, "description": "prueba" }  →  Servidor 1 (vuelve al inicio)
```

### 3. Simular la caída de un servidor
```
POST /servers/2/down
POST /request  →  el Servidor 2 no debe aparecer en las respuestas
```

### 4. Reactivar un servidor
```
POST /servers/2/up
POST /request  →  el Servidor 2 vuelve a recibir peticiones
```

### 5. Consultar solo servidores activos
```
GET /servers/active
```

### 6. Reiniciar todos los contadores
```
POST /servers/reset
GET  /servers  →  todos los contadores deben aparecer en 0
```

---

## Algoritmo Round Robin

La función `get_next_server()` selecciona el siguiente servidor activo de forma circular:

```python
def get_next_server():
    global current_index
    total = len(servers)
    for _ in range(total):
        server = servers[current_index]
        current_index = (current_index + 1) % total
        if server["active"]:
            return server
    return None
```

El operador `%` (módulo) es lo que hace el ciclo circular: cuando el índice llega al último servidor, vuelve automáticamente al primero. Si todos los servidores están inactivos, la función retorna `None` y el endpoint responde con error `503`.

---

## Tecnologías usadas

| Herramienta | Descripción |
|-------------|-------------|
| Python 3    | Lenguaje de programación |
| FastAPI     | Framework para construir la API REST |
| Uvicorn     | Servidor ASGI para ejecutar la aplicación |
| Pydantic    | Validación automática de los datos de entrada |

---

## Materia

Sistemas Operativos
