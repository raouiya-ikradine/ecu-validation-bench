import threading
import time
import isotp

# Sessions de diagnostic
SESSION_DEFAULT = 0x01
SESSION_EXTENDED = 0x03

# Codes de réponse négative (NRC)
NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_INCORRECT_LENGTH = 0x13
NRC_REQUEST_OUT_OF_RANGE = 0x31
NRC_SERVICE_NOT_SUPPORTED_IN_SESSION = 0x7F

# Données lisibles par leur identifiant (DID)
DIDS = {
    0xF190: b"BENCHECU000000001",   # numéro VIN (17 caractères)
    0xF18C: b"SN-2026-0001",        # numéro de série
}

# Codes défaut : (code sur 3 octets, octet de statut)
DTCS = [
    (bytes([0x01, 0x17, 0x00]), 0x09),   # P0117 : capteur de température, signal bas
    (bytes([0x02, 0x17, 0x00]), 0x08),   # P0217 : surchauffe moteur
]


class UdsServer:
    """Serveur de diagnostic UDS : écoute sur 0x7E0, répond sur 0x7E8."""

    def __init__(self, bus, rxid=0x7E0, txid=0x7E8):
        address = isotp.Address(isotp.AddressingMode.Normal_11bits,
                                rxid=rxid, txid=txid)
        self.stack = isotp.CanStack(bus, address=address)   # couche ISO-TP
        self.session = SESSION_DEFAULT
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    # ---------- boucle principale ----------
    def _run(self):
        while not self._stop.is_set():
            self.stack.process()                  # fait avancer ISO-TP
            if self.stack.available():
                request = self.stack.recv()       # une requête UDS complète
                response = self.handle(request)
                if response is not None:
                    self.stack.send(response)
            time.sleep(0.001)

    # ---------- aiguillage selon le service ----------
    def handle(self, req):
        if len(req) == 0:
            return None
        sid = req[0]
        if sid == 0x10:
            return self._session_control(req)
        if sid == 0x22:
            return self._read_did(req)
        if sid == 0x19:
            return self._read_dtc(req)
        return self._negative(sid, NRC_SERVICE_NOT_SUPPORTED)

    @staticmethod
    def _negative(sid, nrc):
        return bytes([0x7F, sid, nrc])            # réponse négative

    # ---------- service 0x10 ----------
    def _session_control(self, req):
        if len(req) != 2:
            return self._negative(0x10, NRC_INCORRECT_LENGTH)
        sub = req[1]
        if sub not in (SESSION_DEFAULT, SESSION_EXTENDED):
            return self._negative(0x10, NRC_SUBFUNCTION_NOT_SUPPORTED)
        self.session = sub
        return bytes([0x50, sub, 0x00, 0x32, 0x01, 0xF4])   # 0x10 + 0x40 = 0x50

    # ---------- service 0x22 ----------
    def _read_did(self, req):
        if len(req) != 3:
            return self._negative(0x22, NRC_INCORRECT_LENGTH)
        did = (req[1] << 8) | req[2]
        if did not in DIDS:
            return self._negative(0x22, NRC_REQUEST_OUT_OF_RANGE)
        return bytes([0x62, req[1], req[2]]) + DIDS[did]    # 0x22 + 0x40 = 0x62

    # ---------- service 0x19 ----------
    def _read_dtc(self, req):
        if len(req) != 3:
            return self._negative(0x19, NRC_INCORRECT_LENGTH)
        if self.session != SESSION_EXTENDED:                # réservé à la session étendue
            return self._negative(0x19, NRC_SERVICE_NOT_SUPPORTED_IN_SESSION)
        if req[1] != 0x02:
            return self._negative(0x19, NRC_SUBFUNCTION_NOT_SUPPORTED)
        mask = req[2]
        response = bytearray([0x59, 0x02, 0xFF])            # 0x19 + 0x40 = 0x59
        for code, status in DTCS:
            if status & mask:
                response += code + bytes([status])
        return bytes(response)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join()