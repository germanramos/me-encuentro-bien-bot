import os
from enum import Enum as _Enum

# all in seconds
ASKING_TIME = int(os.environ.get('ASKING_TIME', 30))
ANSWER_TIME = int(os.environ.get('ANSWER_TIME', 10))
BED_TIME    = int(os.environ.get('BED_TIME'   , 60))
DB_FILE = os.environ.get('DB_FILE', 'meencuentrobien.db')

class Status(_Enum):
    ESPERANDO_A_HACER_PING = 1
    ESPERANDO_RESPUESTA = 2
    ALARMA_ENVIADA = 3
    DURMIENDO = 4
