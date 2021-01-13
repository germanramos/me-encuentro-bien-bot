import os
from enum import Enum as _Enum

# all in seconds
ASKING_TIME = int(os.environ.get('ASKING_TIME', 30))
SHOWER_TIME = int(os.environ.get('SHOWER_TIME', ASKING_TIME/5 ))
ANSWER_TIME = int(os.environ.get('ANSWER_TIME', 10))
BED_TIME    = int(os.environ.get('BED_TIME'   , 60))
CHECK_TIME  = int(os.environ.get('CHECK_TIME' , 5))
DB_FILE = os.environ.get('DB_FILE', 'meencuentrobien.db')

class Status(_Enum):
    ESPERANDO_A_HACER_PING = 1
    ESPERANDO_RESPUESTA = 2
    ALARMA_ENVIADA = 3
    DURMIENDO = 4
    
asking_texts = [
    "¿Como estás?",
    "¿Que tal estás?",
    "¿Que tal andas?",
    "¿Como llevas el día?",
    "¿Que tal vas?",
]

morning_texts = [
    "Buenos días, ¿Qué tal has dormido?",
    "Buenos días, ya es hora de despertar"
    "¡A despertar! Que pases un día estupendo"
    "¡Hola! Que pases un feliz día!"
]

night_texts = [
    "Buenas noches, que tengas felices sueños",
    "Espero que duermas muy bien",
    "Buenas noches, a contar ovejitas!"
    "Camino de la cama, es el mejor camino ;-)"
]

answer_texts = [
    "Me alegro de que estes bien",
    "Ok",
    "Entiendo",
    "Vale",
    "Tomo nota",
    "Me quedo mas tranquilo"
]