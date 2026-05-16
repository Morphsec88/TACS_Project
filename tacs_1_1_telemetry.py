import os
import time

class LowLevelTelemetry:
    def __init__(self):
        pass

    def capture_snapshot(self):
        class Snapshot:
            def __init__(self):
                try:
                    # Windows WMI alapú CPU sebesség lekérdezés és tisztítás
                    cmd_freq = os.popen("wmic cpu get CurrentClockSpeed").read()
                    lines_freq = cmd_freq.split()
                    if len(lines_freq) >= 2:
                        self.cpu_frequency_mhz = float(lines_freq[1])
                    else:
                        self.cpu_frequency_mhz = 2600.0

                    # Windows WMI alapú terheltség lekérdezés és tisztítás
                    cmd_load = os.popen("wmic cpu get LoadPercentage").read()
                    lines_load = cmd_load.split()
                    if len(lines_load) >= 2:
                        self.cpu_usage_percent = float(lines_load[1])
                    else:
                        self.cpu_usage_percent = 12.5
                        
                except Exception:
                    # Biztonsági tartalék értékek hiba esetére
                    self.cpu_frequency_mhz = 2600.0
                    self.cpu_usage_percent = 12.5
                    
        return Snapshot()

# --- TESZTFUTTATÁS AZ IDLE F5-HÖZ ---
if __name__ == "__main__":
    print("[+] TACS Alacsony szintű telemetria indítása...")
    telemetry = LowLevelTelemetry()
    
    # 3 gyors mintavétel tesztelésként
    for i in range(3):
        snap = telemetry.capture_snapshot()
        print(f"[Minta {i+1}] CPU Órajel: {snap.cpu_frequency_mhz} MHz | Terheltség: {snap.cpu_usage_percent}%")
        time.sleep(1)
