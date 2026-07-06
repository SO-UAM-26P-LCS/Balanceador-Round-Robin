from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -------------------------------------------------------
# Creación de la aplicación
# -------------------------------------------------------
app = FastAPI(
    title="Balanceador Round Robin",
    description="API REST para simular un balanceador de carga",
    version="1.0"
)


# -------------------------------------------------------
# Modelo de datos
# -------------------------------------------------------
# Representa una petición enviada por el cliente.
# Funciona como un DTO: define qué datos viajan entre
# cliente y servidor.
class RequestMessage(BaseModel):
    id: int
    description: str


# -------------------------------------------------------
# Lista de servidores simulados
# -------------------------------------------------------
# Ejercicio 1: se agregaron el Servidor 4 y el Servidor 5
servers = [
    {"id": 1, "name": "Servidor 1", "active": True, "requests": 0},
    {"id": 2, "name": "Servidor 2", "active": True, "requests": 0},
    {"id": 3, "name": "Servidor 3", "active": True, "requests": 0},
    {"id": 4, "name": "Servidor 4", "active": True, "requests": 0},
    {"id": 5, "name": "Servidor 5", "active": True, "requests": 0}
]

current_index = 0


# -------------------------------------------------------
# Algoritmo Round Robin
# -------------------------------------------------------
def get_next_server():
    global current_index
    total = len(servers)

    for _ in range(total):
        server = servers[current_index]
        current_index = (current_index + 1) % total
        if server["active"]:
            return server

    return None


# -------------------------------------------------------
# Endpoints de la API
# -------------------------------------------------------

@app.get("/servers")
def get_servers():
    return servers


@app.post("/request")
def receive_request(message: RequestMessage):
    server = get_next_server()

    if server is None:
        raise HTTPException(
            status_code=503,
            detail="No hay servidores disponibles"
        )

    server["requests"] += 1

    return {
        "request_id": message.id,
        "description": message.description,
        "assigned_server": server["name"],
        "server_id": server["id"]
    }


@app.post("/servers/{server_id}/down")
def server_down(server_id: int):
    for server in servers:
        if server["id"] == server_id:
            server["active"] = False
            return {
                "message": f"{server['name']} desactivado"
            }

    raise HTTPException(
        status_code=404,
        detail="Servidor no encontrado"
    )


@app.post("/servers/{server_id}/up")
def server_up(server_id: int):
    for server in servers:
        if server["id"] == server_id:
            server["active"] = True
            return {
                "message": f"{server['name']} activado"
            }

    raise HTTPException(
        status_code=404,
        detail="Servidor no encontrado"
    )


# -------------------------------------------------------
# Ejercicio 2: reiniciar contadores de peticiones
# -------------------------------------------------------
@app.post("/servers/reset")
def reset_servers():
    for server in servers:
        server["requests"] = 0

    return {
        "message": "Contadores de peticiones reiniciados"
    }


# -------------------------------------------------------
# Ejercicio 3: devolver únicamente los servidores activos
# -------------------------------------------------------
@app.get("/servers/active")
def get_active_servers():
    activos = [server for server in servers if server["active"]]
    return activos
