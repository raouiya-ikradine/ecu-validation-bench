import threading
import cantools


class DashboardEcu:
    """ECU dashboard simulé : reçoit ENGINE_STATUS, le décode et l'affiche."""

    def __init__(self, bus, dbc_path="dbc/network.dbc", timeout=0.5, verbose=True):
        self.bus = bus
        self.db = cantools.database.load_file(dbc_path)
        self.engine_msg = self.db.get_message_by_name("ENGINE_STATUS")
        self.timeout = timeout          # sans trame pendant ce délai, le moteur est "muet"
        self.verbose = verbose
        self.last_values = None         # dernières valeurs décodées
        self.engine_alive = False
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.is_set():
            frame = self.bus.recv(timeout=self.timeout)       # python-can : recv

            if frame is None:                                  # rien reçu dans le délai
                if self.engine_alive and self.verbose:
                    print("Dashboard : ECU moteur muet !")
                self.engine_alive = False
                continue

            if frame.arbitration_id != self.engine_msg.frame_id:
                continue                                       # message qui ne m'intéresse pas

            self.last_values = self.db.decode_message(         # cantools : decode
                frame.arbitration_id, frame.data)
            self.engine_alive = True

            if self.verbose:
                v = self.last_values
                print(f"Dashboard | {v['EngineSpeed']} rpm | "
                      f"{v['CoolantTemp']} degC | charge {v['EngineLoad']} %")

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()