import time
import can
import isotp
from uds.server import UdsServer

bus_serveur = can.Bus(interface="virtual", channel="diag")
bus_testeur = can.Bus(interface="virtual", channel="diag")

serveur = UdsServer(bus_serveur)
serveur.start()

# Le testeur a les adresses inversées par rapport au serveur
adresse = isotp.Address(isotp.AddressingMode.Normal_11bits, rxid=0x7E8, txid=0x7E0)
testeur = isotp.CanStack(bus_testeur, address=adresse)


def demander(requete, attente=1.0):
    testeur.send(requete)
    debut = time.time()
    while time.time() - debut < attente:
        testeur.process()
        if testeur.available():
            return testeur.recv()
        time.sleep(0.001)
    return None


essais = [
    ("Lire le VIN", bytes([0x22, 0xF1, 0x90])),
    ("Lire un DID inconnu", bytes([0x22, 0x12, 0x34])),
    ("Service inconnu", bytes([0x27, 0x01])),
    ("Lire les DTC en session par défaut", bytes([0x19, 0x02, 0xFF])),
    ("Passer en session étendue", bytes([0x10, 0x03])),
    ("Lire les DTC en session étendue", bytes([0x19, 0x02, 0xFF])),
]

for nom, req in essais:
    rep = demander(req)
    print(nom)
    print("   requête :", req.hex(" "))
    print("   réponse :", rep.hex(" ") if rep else "aucune")

serveur.stop()
bus_serveur.shutdown()
bus_testeur.shutdown()