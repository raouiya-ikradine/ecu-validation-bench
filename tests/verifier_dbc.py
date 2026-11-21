import cantools

# 1. Charger le DBC (cantools LIT le fichier)
db = cantools.database.load_file("dbc/network.dbc")

# 2. Afficher ce que cantools a compris
for m in db.messages:
    print(hex(m.frame_id), m.name, m.length, "octets")
    for s in m.signals:
        print("   ", s.name, "| début", s.start, "| longueur", s.length,
              "| facteur", s.scale, "| offset", s.offset, "|", s.unit)

# 3. Encoder : valeurs réelles vers octets
msg = db.get_message_by_name("ENGINE_STATUS")
data = msg.encode({"EngineSpeed": 3000, "CoolantTemp": 90, "EngineLoad": 45.5})
print("Encodé :", data.hex(" "))

# 4. Décoder : octets vers valeurs réelles
print("Décodé :", db.decode_message(msg.frame_id, data))