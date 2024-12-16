# API de SG GPT

Esta documentación detalla cómo utilizar esta API. Proporciona información sobre el formato del endpoint, la estructura del cuerpo de la solicitud, los parámetros necesarios y los posibles valores de respuesta.

## Endpoints

### `POST /run/json`

Este endpoint permite crear respuestas basadas en la información introducida por el usuario. Esta API se basa en el modelo de reconocimiento de entidades con nombre GliNER.

#### Parámetros 
`message`: Entrada del usuario \
`number_of_response`: Número máximo de respuestas a generar 


#### Cuerpo de la solicitud

El cuerpo de la solicitud debe contener un JSON con los siguientes campos (incluyen ejemplo de datos):

```json
{
  "message": "Enter a user query",
  "number_of_response": 100
}
```

#### Respuesta  

Si la solicitud es exitosa, el servidor devolverá un JSON como lista con las respuestas.

#### Ejemplo de respuesta:

```json
[
  {
    "@id": "1",
    "id": 1822,
    "version": 0,
    "name": "AERO_1",
    "description": "",
    "insertDate": "2024-11-26T19:56:16.808490309Z",
    "nemonic": "1732650976lh05tBZiZV",
    "identificator": "SANTANDER_AERO_1",
    "active": true,
    "physicalPath": "SANTANDER||9308",
    "template": {
      "@id": "2",
      "id": 414,
      "version": 0,
      "name": "Aero",
      "description": "Plantilla para Aeros",
      "icon": "icon-id-aero",
      "insertDate": "2024-11-26T19:55:43.290334006Z",
      "nemonic": "AeroNemonic",
      "assetOrganized": false,
      "templateOrganized": false,
      "type": "Complex",
      "numComplexAttributes": 0,
      "final": false,
      "abstract": false
    },
    "numComplexAssets": 0
  }
]
```

#### Ejemplo de respuesta (sin éxito, 404):
```json
[
  {
    "Warning": "No content found, please search differently again."
  }
]
```


#### Campos de la respuesta:

- `number_of_response`: Número máximo de respuestas  
- `message`: User query    
    > Ejemplos:  
    - Find me all the aerogeneradores in Santander's park  
    - Find turbina for Aero 23 for Leganes  
    - For Sante get velocidad viento for Aero 6  
    - Por el parque Ourense dame velocidad viento por Aero 6  
    - Por el parque Ourense dame energia consumida por Aero 6  
    - Dame los aeros de Santander que contengan 12 en el nombre
    - Busca la turbina del aero_1 del parque de santander
    - Muéstrame todos los parques
    - Dame para el aero 3 de Oviedo la velocidad del viento
    - Dame para el aero 3 de Oviedo la energia producida


### `POST /run/form`

Este endpoint es el mismo que el anterior, excepto que las entradas son de estilo formulario en lugar de json.

## Códigos de estado

`200`: Respuesta exitosa. Contiene las predicciones en el cuerpo de la respuesta.  
`404`: No se ha encontrado. No se ha encontrado contenido para esta entrada de usuario. Prueba con otra consulta.  
`422`: Error de validación. Indica que algún campo obligatorio está ausente o tiene un formato incorrecto.  
`500`: Error interno de servidor. Expresa un problema interno en la ejecución del código, principalmente no contemplado previamente, y expresado en los logs a través de excepciones.
