import time
import can
from ecus.engine_ecu import EngineEcu
from ecus.dashboard_ecu import DashboardEcu

# Un accès au bus par ECU, tous deux sur le même channel
bus_moteur = can.Bus(interface="virtual", channel="reseau")
bus_dash = can.Bus(interface="virtual", channel="reseau")

moteur = EngineEcu(bus_moteur)
dash = DashboardEcu(bus_dash)

dash.start()          # le dashboard se met à l'écoute en premier
moteur.start()
time.sleep(1)         # le réseau tourne pendant 1 seconde

moteur.stop()         # on coupe le moteur : le dashboard doit s'en apercevoir
time.sleep(1)

dash.stop()
bus_moteur.shutdown()
bus_dash.shutdown()