import time
# Beimportáljuk a szomszédos 1/1-es fájlt, ezért kell egy mappában lenniük!
from tacs_1_1_telemetry import LowLevelTelemetry

class NoiseBaselineProfiler:
    def __init__(self, telemetry_module: LowLevelTelemetry):
        self.telemetry = telemetry_module
        self.frequency_samples = []
        self.usage_samples = []

    def run_profiling(self, sample_count: int = 10, delay: float = 0.2):
        """Összegyűjti az alapzaj mintákat a kalibrációhoz"""
        print(f"[!] Alapzaj mérése indul ({sample_count} minta, {delay}s lépésközzel)...")
        print("[!] Kérjük, ne mozgassa az egeret és ne futtasson más programot!")
        
        for _ in range(sample_count):
            snapshot = self.telemetry.capture_snapshot()
            if snapshot.cpu_frequency_mhz > 0:
                self.frequency_samples.append(snapshot.cpu_frequency_mhz)
            self.usage_samples.append(snapshot.cpu_usage_percent)
            time.sleep(delay)
            
        print("[+] Mintavétel sikeresen lezárult.")

    def calculate_baseline(self) -> dict:
        """Kiszámítja a statisztikai középértékeket és a varianciát (ingadozást)"""
        if not self.frequency_samples:
            return {"status": "Hiba: Nincs elegendő hardveres adat."}
            
        avg_freq = sum(self.frequency_samples) / len(self.frequency_samples)
        avg_use = sum(self.usage_samples) / len(self.usage_samples)
        
        # Max és min kilengések az áramköri tüskék kalibrálásához
        max_freq_spike = max(self.frequency_samples) - avg_freq
        
        return {
            "Átlagos_Órajel_MHz": round(avg_freq, 2),
            "Átlagos_Terheltség_Százalék": round(avg_use, 2),
            "Kritikus_Frekvencia_Kilengés_MHz": round(max_freq_spike, 2),
            "Ajánlott_Zajgenerálási_Küszöb": "ALACSONY (IdeaPad 100 optimalizált)"
        }

if __name__ == "__main__":
    print("[+] TACS 1/2 Modul: Alapzaj-analizátor inicializálása.")
    
    # Kapcsolódás az 1/1-es alacsony szintű modulhoz
    engine_1_1 = LowLevelTelemetry()
    profiler = NoiseBaselineProfiler(engine_1_1)
    
    # Profilozás futtatása
    profiler.run_profiling(sample_count=15, delay=0.2)
    report = profiler.calculate_baseline()
    
    print("\n=== HARDVERES ALAPZAJ JELENTÉS ===")
    for kulcs, ertek in report.items():
        print(f"{kulcs}: {ertek}")
    print("===================================\n")
