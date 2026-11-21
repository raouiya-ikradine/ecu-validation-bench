import can

bus_tx = can.Bus(interface="virtual", channel="test_bus")
bus_rx = can.Bus(interface="virtual", channel="test_bus")

for i in range(3):
    msg = can.Message(arbitration_id=0x100,
                      data=[i, 0x00, 0x00, 0x00],
                      is_extended_id=False)
    bus_tx.send(msg)
    print("Envoyé :", msg)

for _ in range(3):
    recu = bus_rx.recv(timeout=1.0)
    print("Reçu   :", recu)

bus_tx.shutdown()
bus_rx.shutdown()