from datetime import datetime, timedelta

from constants import Status

_people = {}
_supervisors = {}

def createPerson(chat_id, name, supervisor):
    _people[chat_id] = { "time": datetime.now(),
                        "status": Status.ESPERANDO_A_HACER_PING, 
                        "name": name, 
                        "supervisor": supervisor
                      }

def updatePerson(chat_id, status):
    _people[chat_id]["time"] = datetime.now()
    _people[chat_id]["status"] = status

def personExists(chat_id):
    return chat_id in _people

def getAllPeople():
    return [ {**p,**{"chat_id":k}} for k,p in _people.items()]

def createSupervisor(chat_id, username):
    _supervisors[username] = chat_id

def getSupervisorChatId(username):
    return _supervisors.get(username, None)

def remove(chat_id, username):
    # del _people[chat_id]
    # del _supervisors[username]
    _people.pop("chat_id", None)
    _supervisors.pop("username", None)
