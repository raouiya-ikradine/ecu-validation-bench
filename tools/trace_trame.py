import can
import cantools

db = cantools.database.load_file("dbc/network.dbc")
msg = db.get_message_by_name("ENGINE_STATUS")

bus_moteur = can.Bus(interface="virtual", channel="trace")
bus_dash = can.Bus(interface="virtual", channel="trace")

print("=== ECU MOTEUR ===")
valeurs = {"EngineSpeed": 3000, "CoolantTemp": 90, "EngineLoad": 45.5}
print("1. Valeurs réelles  :", valeurs)

octets = msg.encode(valeurs)
print("2. cantools.encode  :", octets.hex(" "), "| ID", hex(msg.frame_id))

trame = can.Message(arbitration_id=msg.frame_id, data=octets, is_extended_id=False)
bus_moteur.send(trame)
print("3. python-can.send  : trame envoyée sur le bus")

print("=== BUS CAN VIRTUEL ===")
print("   la trame circule :", hex(trame.arbitration_id), trame.data.hex(" "))

print("=== ECU DASHBOARD ===")
recue = bus_dash.recv(timeout=1.0)
print("4. python-can.recv  :", hex(recue.arbitration_id), recue.data.hex(" "))

decode = db.decode_message(recue.arbitration_id, recue.data)
print("5. cantools.decode  :", decode)

print("6. Affichage        : Dashboard |", decode["EngineSpeed"], "rpm |",
      decode["CoolantTemp"], "degC | charge", decode["EngineLoad"], "%")

bus_moteur.shutdown()
bus_dash.shutdown()