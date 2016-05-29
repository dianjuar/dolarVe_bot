from json import loads
from datetime import datetime
from threading import Thread
import urllib2

endpoint = "https://s3.amazonaws.com/dolartoday/data.json"
update_delay = 1800
last_update = None
data = None
old_data = None
updating_flag = False



def createUpdatingThread():
    """Create a thread that updates data"""
    thread = Thread(target=updateData)
    thread.daemon = True
    thread.start()

def updateData():
    """Updates data via the endpoint provided
    data is cached into old_data to avoid race conditions when updating data via thread
    """
    global old_data
    global data
    global last_update
    global updating_flag
    old_data = data
    updating_flag = True
    try:
        request = urllib2.Request(endpoint)
        response = urllib2.urlopen(request,timeout=30)
        data = loads(response.read().decode('latin-1'))
        last_update = datetime.now()
    except urllib2.URLError, e:
        print("Actualizacion Fallida: %r" % e)
    updating_flag = False

def get_dolar():
    """Gets dollar value
    calls checkTimeout before returning the value
    if the updating thread is running signalled by updating_flag, data is retrieved from old_data instead
    """
    if not updating_flag:
        checkTimeout()
        return data['USD']['efectivo_real']
    else:
        return old_data['USD']['efectivo_real']

def checkTimeout():
    """Checks if the timeout in seconds has passed since the last update
    if last_update or data is None calls updateData to force updating the data before letting a get_xxx method run

    if the timeout has been completed, createUpdatingThread is called
    """
    if last_update is None or data is None:
        updateData()
        return
    delta = datetime.now() - last_update
    if delta.seconds > update_delay:
        createUpdatingThread()
    else:
        return
