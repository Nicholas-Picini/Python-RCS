import pymem
import pymem.process
import time
import math
import keyboard
from os import _exit
import requests
import re


r = requests.get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.hpp")
r = r.text


offsets = ['dwLocalPlayer', 'm_iShotsFired',
           'm_aimPunchAngle', 'dwClientState', 'dwClientState_ViewAngles']


d = {}
offs = []
for i in range(len(offsets)):
    if offsets[i] in r:
        search = re.findall(str(offsets[i]) + '\s'"= (.*);", r)
        offs += search


i = 0
while i <= len(offsets)-1:
    (key, val) = offsets[i], offs[i]
    d[key] = val
    i += 1


m_iShotsFired = int(d['m_iShotsFired'], base = 16)
m_aimPunchAngle = int(d['m_aimPunchAngle'], base = 16)
dwClientState = int(d['dwClientState'], base = 16)
dwLocalPlayer = int(d['dwLocalPlayer'], base = 16)
dwClientState_ViewAngles = int(d['dwClientState_ViewAngles'], base = 16)


pm = pymem.Pymem("csgo.exe")
client = pymem.process.module_from_name(pm.process_handle, "client_panorama.dll").lpBaseOfDll
engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll


rcsonoff = True


def normalizeAngles(viewAngleX, viewAngleY):
    if viewAngleX > 89:
        viewAngleX -= 360
    if viewAngleX < -89:
        viewAngleX += 360
    if viewAngleY > 180:
        viewAngleY -= 360
    if viewAngleY < -180:
        viewAngleY += 360
    return viewAngleX, viewAngleY


def checkangles(x, y):
    if x > 89:
        return False
    elif x < -89:
        return False
    elif y > 360:
        return False
    elif y < -360:
        return False
    else:
        return True


def nanchecker(first, second):
    if math.isnan(first) or math.isnan(second):
        return False
    else:
        return True


def main():
    print('rcs is running')
    global amount
    oldpunchx = 0.0
    oldpunchy = 0.0
    while True:
        time.sleep(0.01)
        if rcsonoff:
            rcslocalplayer = pm.read_int(client + dwLocalPlayer)
            rcsengine = pm.read_int(engine + dwClientState)
            if pm.read_int(rcslocalplayer + m_iShotsFired) > 2:
                rcs_x = pm.read_float(rcsengine + dwClientState_ViewAngles)
                rcs_y = pm.read_float(rcsengine + dwClientState_ViewAngles + 0x4)
                punchx = pm.read_float(rcslocalplayer + m_aimPunchAngle)
                punchy = pm.read_float(rcslocalplayer + m_aimPunchAngle + 0x4)
                newrcsx = rcs_x - (punchx - oldpunchx) * 2
                newrcsy = rcs_y - (punchy - oldpunchy) * 2
                newrcs, newrcy = normalizeAngles(newrcsx, newrcsy)
                oldpunchx = punchx
                oldpunchy = punchy
                if nanchecker(newrcsx, newrcsy) and checkangles(newrcsx, newrcsy):
                    pm.write_float(rcsengine + dwClientState_ViewAngles, newrcsx)
                    pm.write_float(rcsengine + dwClientState_ViewAngles + 0x4, newrcsy)
            else:
                oldpunchx = 0.0
                oldpunchy = 0.0
                newrcsx = 0.0
                newrcsy = 0.0
            if keyboard.is_pressed('delete'):
                _exit(0)


if __name__ == '__main__':
    main()
