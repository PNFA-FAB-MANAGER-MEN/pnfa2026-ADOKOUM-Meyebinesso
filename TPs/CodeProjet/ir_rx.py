
```python
# ir_rx.py - Décodeur IR NEC non-bloquant pour MicroPython
import utime
from machine import Pin

class NEC_RX:
    def __init__(self, pin, callback):
        self.pin = pin
        self.callback = callback
        self.pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._cb)
        self.edge_ticks = []
        
    def _cb(self, pin):
        self.edge_ticks.append(utime.ticks_us())
        if len(self.edge_ticks) >= 67:
            # Traitement du signal une fois le paquet complet
            ticks = self.edge_ticks
            self.edge_ticks = []
            self._decode(ticks)

    def _decode(self, ticks):
        durations = [utime.ticks_diff(ticks[i+1], ticks[i]) for i in range(len(ticks)-1)]
        
        # Vérification de la trame de tête NEC (9ms LOW + 4.5ms HIGH)
        if not (8000 < durations[0] < 10000 and 4000 < durations[1] < 5000):
            return

        data = 0
        for i in range(3, 67, 2):
            data <<= 1
            if durations[i] > 1000: # Intervalle long (~1.68ms) = bit 1
                data |= 1

        # Extraction de l'adresse et de la commande (8-bit)
        cmd = (data >> 8) & 0xFF
        addr = (data >> 24) & 0xFF
        
        # Appel de la fonction utilisateur avec le code reçu
        self.callback(cmd, addr)

```