import threading
import can
import cantools


class EngineEcu:
    """ECU moteur simulé : envoie ENGINE_STATUS toutes les 100 ms."""

    def __init__(self, bus, dbc_path="dbc/network.dbc", period=0.1):
        self.bus = bus
        self.db = cantools.database.load_file(dbc_path)
        self.msg = self.db.get_message_by_name("ENGINE_STATUS")
        self.period = period
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _values(self, step):
        # Valeurs simulées qui varient à chaque envoi
        return {
            "EngineSpeed": 800 + (step * 50) % 3000,
            "CoolantTemp": 70 + (step // 10) % 30,
            "EngineLoad": 20 + (step % 40) * 1.5,
        }

    def _run(self):
        step = 0
        while not self._stop.is_set():
            data = self.msg.encode(self._values(step))            # cantools : encode
            frame = can.Message(arbitration_id=self.msg.frame_id,
                                data=data, is_extended_id=False)
            self.bus.send(frame)                                   # python-can : send
            step += 1
            self._stop.wait(self.period)                           # pause de 100 ms

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()


if __name__ == "__main__":
    # Petit test : l'ECU envoie, un lecteur reçoit et décode
    bus_ecu = can.Bus(interface="virtual", channel="reseau")
    bus_lecteur = can.Bus(interface="virtual", channel="reseau")

    ecu = EngineEcu(bus_ecu, period=0.5)
    ecu.start()

    db = cantools.database.load_file("dbc/network.dbc")
    for _ in range(10):
        frame = bus_lecteur.recv(timeout=1.0)
        if frame is None:
            print("Aucune trame reçue (ECU muet ?)")
            break
        print(hex(frame.arbitration_id),
              db.decode_message(frame.arbitration_id, frame.data))

    ecu.stop()
    bus_ecu.shutdown()
    bus_lecteur.shutdown()