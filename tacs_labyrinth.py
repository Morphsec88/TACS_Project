import socket
import threading
import random

# A teljes hálózati zóna, ahol a labirintus felépül
START_PORT = 7720
END_PORT = 7740
PORT_TARTOMANY = list(range(START_PORT, END_PORT + 1))

# A hacker által már megérintett (lebuktatott) portok halmaza
erintett_portok = set()
lock = threading.Lock()

def kiertekel_biztonsagi_matrix(port):
    """Kiszámítja, hogy a hacker mozgása alapján hol kell lennie a valódi kapunak"""
    global erintett_portok
    with lock:
        # Hozzáadjuk az éppen megszólított portot a lebukott portok listájához
        erintett_portok.add(port)
        
        # Kilistázzuk a még teljesen érintetlen, szűz portokat
        szuz_portok = [p for p in PORT_TARTOMANY if p not in erintett_portok]
        
        # Ha a hacker már mindent körbepásztázott, nincs biztonságos zóna -> a kapu megsemmisült
        if not szuz_portok:
            return None
            
        # A VALÓDI KAPU mindig az érintetlen terület abszolút közepe (Dinamikus Közép)
        # Így ha a hacker két szélről rohan befelé, a kapu folyamatosan kitér előle
        kozep_index = len(szuz_portok) // 2
        dinamikus_valodi_kapu = szuz_portok[kozep_index]
        
        return dinamikus_valodi_kapu

def kezel_kapu_kommunikacio(kliens_socket, port, cim):
    # Megnézzük, hogy a hacker jelenlegi pozíciója mellett hol áll a védelmi vonal
    aktualis_valodi_kapu = kiertekel_biztonsagi_matrix(port)
    
    try:
        # A hacker CSAK akkor tudna belépni, ha a saját pásztázása SOHA nem ért volna hozzá a portjához, 
        # és pontosan eltalálná a menekülő dinamikus közepet (ami lineáris keresésnél matematikai képtelenség)
        if port == aktualis_valodi_kapu and port not in erintett_portok:
            print(f"\n[SIKER] Hiteles ugrókód észlelve a dinamikus középponton: {port}!")
            kliens_socket.send(b"WELCOME_TO_TACS_QUANTUM_CORE\n")
        else:
            # Minden más esetben ömlik a hamis bináris struktúra, elfedve a valóságot
            print(f"[LABIRINTUS] Szimmetrikus frontvonal észlelve a(z) {port}-es porton a(z) {cim} címről. (Valódi kapu most: {aktualis_valodi_kapu})")
            
            # Azonnali nem-sablon bináris zaj kiküldése (időzítések nélkül)
            kliens_socket.send(b"\x03\x01" + random.randbytes(4) + b"\xef\x00\x31")
            
    except Exception:
        pass
    finally:
        kliens_socket.close()

def ajto_figyelo(port):
    """Ez a szál felelős egyetlen konkrét port nyitvatartásáért és figyeléséért"""
    szerver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Megengedjük a port azonnali újrafelhasználását újraindításkor
        szerver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        szerver.bind(("0.0.0.0", port))
        szerver.listen(10)
        while True:
            kliens_socket, cim = szerver.accept()
            threading.Thread(target=kezel_kapu_kommunikacio, args=(kliens_socket, port, cim), daemon=True).start()
    except Exception:
        pass

def indit_kvantum_labirintus():
    print(f"[*] TACS Kvantum-Ösvény inicializálása {START_PORT} és {END_PORT} között...")
    for port in PORT_TARTOMANY:
        # Minden porthoz elindítunk egy önálló háttérfigyelőt
        threading.Thread(target=ajto_figyelo, args=(port,), daemon=True).start()
    print("[*] A szimmetrikus csapda aktív. A valódi kapu folyamatosan elmozdul a pásztázás elől.")

if __name__ == "__main__":
    indit_kvantum_labirintus()
    # Ez a sor tartja életben a főprogramot a memóriában
    threading.Event().wait()
