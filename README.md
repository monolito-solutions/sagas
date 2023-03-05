# Inbound - Monolito Solutions

Este es el repositorio del microservicio Inbound del proyecto "Entregas de los Alpes", el cual se encarga de recibir los pedidos del cliente. Este microservicio fue construido utilizando el framework FastAPI.

## Requerimientos

Para poder correr el microservicio Inbound, es necesario tener instalado lo siguiente:

- Python 3.10 o superior
- pip

Además, se necesitará instalar las dependencias del proyecto utilizando el siguiente comando:

```
pip install -r requirements.txt
```

## Configuración

Antes de correr el microservicio Inbound, es necesario configurar las direcciones del host de Apache Pulsar y la base de datos MySQL.
- La configuración de Apache Pulsar se encuentra en ```./utils.py```
- La configuración de la base de datos MySQL se encuentra en ```./config/db.py```

## Correr el microservicio

Para correr el microservicio Inbound, use el siguiente comando:

```
python main.py
```

Una vez que el microservicio esté corriendo, se podrá hacer una petición HTTP POST al endpoint `/orders` para enviar un pedido al microservicio. El pedido debe incluir un formato similar a los encontrados en la carpeta de ```./json_examples```.
