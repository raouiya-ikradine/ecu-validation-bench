import can

# ---------- Expérience A : le timeout ----------
bus_tx = can.Bus(interface="virtual", channel="exp_timeout")
bus_rx = can.Bus(interface="virtual", channel="exp_timeout")

# On n'envoie rien : que renvoie recv() ?
recu = bus_rx.recv(timeout=1.0)
print("A - Rien envoyé, recv() renvoie :", recu)

bus_tx.shutdown()
bus_rx.shutdown()

# ---------- Expérience B : le filtre ----------
bus_tx = can.Bus(interface="virtual", channel="exp_filtre")
bus_rx = can.Bus(interface="virtual", channel="exp_filtre",
                 can_filters=[{"can_id": 0x100, "can_mask": 0x7FF}])

# On envoie une trame 0x100 et une trame 0x200
bus_tx.send(can.Message(arbitration_id=0x100, data=[1, 2, 3, 4], is_extended_id=False))
bus_tx.send(can.Message(arbitration_id=0x200, data=[5, 6, 7, 8], is_extended_id=False))

print("B - 1er recv :", bus_rx.recv(timeout=1.0))
print("B - 2e recv  :", bus_rx.recv(timeout=1.0))

bus_tx.shutdown()
bus_rx.shutdown()