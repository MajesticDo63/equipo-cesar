# Sistema de Gestión de Inventario

Equipo: Cesar Eduardo Valdez Pinto  
Dominio: Dominio 3 — Sistema de Gestión de Inventario  
Fecha: Abril 2026

## Qué problema resuelve?
Este sistema permite a una empresa controlar su inventario de productos en tiempo real. Registra entradas y salidas de mercancía, monitorea el stock actual de cada producto y genera alertas automáticas cuando un producto cae por debajo del stock mínimo establecido.

## Estructura de la Base de Datos
| Tabla | Descripción | Relación |
|-------|-------------|----------|
| productos | Almacena los productos con su stock actual y mínimo | Base de movimientos y alertas |
| movimientos | Registra cada entrada o salida de inventario | Se relaciona con productos via producto_id |
| alertas | Guarda las alertas de reposición generadas | Se relaciona con productos via producto_id |

## Rutas de la API
| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | / | Interfaz HTML principal |
| POST | /productos | Registrar un producto nuevo |
| GET | /productos | Consultar stock actual de todos los productos |
| POST | /movimiento | Registrar entrada o salida de inventario |
| GET | /bajostock | Ver productos bajo stock mínimo |

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?
La tarea pesada ocurre cuando se registra una salida de inventario y el stock resultante queda por debajo del mínimo. En ese momento el sistema genera una alerta de reposición que incluye un `time.sleep(5)` simulando el proceso costoso de notificar al área de compras. Esto bloquea el sistema porque Flask por defecto atiende una petición a la vez, por lo que mientras se procesa esta alerta ningún otro usuario puede usar la aplicación.

## Cómo levantar el proyecto
```bash
# 1. Clonar el repositorio
git clone https://github.com/MajesticDo63/equipo-cesar.git

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen
docker build -t inventario-app .

# 4. Correr el contenedor
docker run -d -p 5000:5000 \
  -e DB_HOST=ENDPOINT_RDS \
  -e DB_USER=admin \
  -e DB_PASSWORD=PASSWORD \
  -e DB_NAME=inventario_db \
  inventario-app

# 5. Abrir en navegador
http://IP_EC2:5000
```

## Decisiones técnicas
Las tablas se diseñaron separando productos, movimientos y alertas para mantener un historial completo de cambios sin modificar registros existentes. El manejo de errores se implementó con bloques try/except en todas las rutas y las conexiones a la base de datos siempre se cierran en el bloque finally para evitar fugas de conexiones. Lo más difícil fue implementar la lógica de movimientos asegurando que el stock nunca quede negativo y que la alerta se genere correctamente solo en salidas que bajen el stock al mínimo.
