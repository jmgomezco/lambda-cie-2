import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
RESULTADOS_TABLE = "resultados"

def lambda_handler(event, context):
    print("EVENTO RECIBIDO:", json.dumps(event))
    # Ejemplo de body recibido:
    # {
    #   "sessionId": "abc123",
    #   "codigo": "A01",
    #   "desc": "Cólera debido a Vibrio cholerae 01, biovar cholerae"
    # }
    try:
        # --- Capturar IP del cliente para HTTP API y REST API ---
        if "requestContext" in event and "http" in event["requestContext"]:
            ip_cliente = event["requestContext"]["http"].get("sourceIp")
        else:
            ip_cliente = event.get("requestContext", {}).get("identity", {}).get("sourceIp")

        # Parsear el cuerpo del evento (JSON)
        body = event.get('body')
        print("BODY recibido:", body)
        if not body:
            print("Body vacío o nulo")
            return response_json(400, {'error': 'Sin datos'})
        try:
            data = json.loads(body)
            print("DATA parseada:", data)
        except Exception as e:
            print("Error al parsear body:", str(e))
            return response_json(400, {'error': 'Formato de body inválido'})

        sessionId = data.get('sessionId')
        codigo = data.get('codigo')
        desc = data.get('desc', '')

        print("Datos extraídos: sessionId:", sessionId, "codigo:", codigo, "desc:", desc)

        if not sessionId or not codigo:
            print("Faltan sessionId o codigo")
            return response_json(400, {'error': 'Faltan sessionId o codigo'})

        # Guardar en tabla resultados
        table = dynamodb.Table(RESULTADOS_TABLE)
        item = {
            'sessionId': sessionId,
            'fecha_hora': datetime.utcnow().isoformat(),  # Mejor registrar hora real
            'codigo': codigo,
            'desc': desc
             }
        print("Item a guardar:", item)
        table.put_item(Item=item)
        print("Item guardado correctamente")

        return response_json(200, {'ok': True})

    except Exception as e:
        print("ERROR INTERNO:", str(e))
        return response_json(500, {'error': 'Error interno', 'details': str(e)})

def response_json(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, ensure_ascii=False)
    }
