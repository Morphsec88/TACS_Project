import socket
import threading
import random
import psutil
import ctypes
import json
import logging
import os
import sys
import time
import subprocess

# ==============================================================================
# TACS_PROJECT ABSZOLÚT ÚTVONAL ARCHITEKTÚRA (NUITKA / PYINSTALLER KOMPATIBILIS)
# ==============================================================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    sajat_exe = [sys.executable]
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sajat_exe = [sys.executable, os.path.abspath(__file__)]

os.chdir(BASE_DIR)
LOG_FILE_PATH = os.path.join(BASE_DIR, 'tacs_project_security.log')
CONFIG_FILE_PATH = os.path.join(BASE_DIR, 'config.json')

# ==============================================================================
# PROFESSZIONÁLIS VÁLLALATI NAPLÓZÁS (LOGGING) BEÁLLÍTÁSA
# ==============================================================================
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ==============================================================================
# WINDOWS RENDSZERGAZDAI JOG (UAC) KÉNYSZERÍTÉSE
# ==============================================================================
def ellenoriz_es_ker_admin_jogot():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            exe_utvonal = sys.executable if getattr(sys, 'frozen', False) else sys.executable
            argumentumok = [os.path.abspath(__file__)] + sys.argv[1:] if not getattr(sys, 'frozen', False) else sys.argv[1:]
            arg_string = " ".join(f'"{a}"' for a in argumentumok)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_utvonal, arg_string, BASE_DIR, 1)
            sys.exit(0)
    except Exception as e:
        logging.critical(f"TACS_Project UAC hiba: {e}")
        sys.exit(1)

ellenoriz_es_ker_admin_jogot()

# ==============================================================================
# KONFIGURÁCIÓ DINAMIKUS BEOLVASÁSA
# ==============================================================================
try:
    with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    
    START_PORT = config["network"]["start_port"]
    END_PORT = config["network"]["end_port"]
    TITKOS_TOKEN = config["security"]["secret_token"].encode('utf-8')
    logging.info("TACS_Project: A konfigurációs fájl sikeresen beolvasva.")
except Exception as e:
    logging.critical(f"TACS_Project: Nem sikerült beolvasni a config.json-t: {e}")
    START_PORT = 7720
    END_PORT = 7740
    TITKOS_TOKEN = b"IDEAPAD_SECURE_TOKEN_2026"

PORT_TARTOMANY = list(range(START_PORT, END_PORT + 1))
erintett_portok = set()
lock = threading.Lock()

# Biztonságos bytearray pool a string-crash elkerülésére
MEMORIA_POOL = [None] * 5
AKTUALIS_POOL_INDEX = 0

# ==============================================================================
# MCAFEE-ŐRSÉG MÓD (TWIN-PROCESS LOGIKA)
# ==============================================================================
def mcafee_orseg_kulon_folyamat():
    logging.info("[ORSEG] A TACS_Project háttér-őrsége elindult. Figyeljük a törzset...")
    
    # Folyamatnév meghatározása a psutil-hoz
    if getattr(sys, 'frozen', False):
        sajat_nev = os.path.basename(sys.executable)
    else:
        sajat_nev = os.path.basename(sys.executable) # python.exe-t keresünk script módban
    
    while True:
        time.sleep(2.0)
        szamlalo = 0
        for p in psutil.process_iter(['name']):
            try:
                if p.info['name'].lower() == sajat_nev.lower():
                    szamlalo += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Script módban (python tacs_core.py) legalább 2 python.exe-nek kell futnia
        if szamlalo < 2:
            logging.warning("[ORSEG] A TACS_Project fő motorját leállították! Újraindítás...")
            subprocess.Popen(sajat_exe + ["--watchdog-respawn"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit(0)

# ==============================================================================
# 1. RÉTEG: KVANTUM-ÖSVÉNY HÁLÓZATI LABIRINTUS LOGIKA
# ==============================================================================
def kiertekel_biztonsagi_matrix(port):
    global erintett_portok
    with lock:
        erintett_portok.add(port)
        szuz_portok = [p for p in PORT_TARTOMANY if p not in erintett_portok]
        if not szuz_portok:
            return None
        return szuz_portok[len(szuz_portok) // 2]

def kezel_kapu_kommunikacio(kliens_socket, port, cim):
    try:
        aktualis_valodi_kapu = kiertekel_biztonsagi_matrix(port)
        if port == aktualis_valodi_kapu and port not in erintett_portok:
            logging.warning(f"Sikeres lokális Zero-Network belépési kísérlet a porton: {port} erről a címről: {cim}")
            kliens_socket.sendall(b"WELCOME_TO_TACS_QUANTUM_CORE\n")
        else:
            logging.info(f"Anomália észlelve: a(z) {cim} cím megérintette a(z) {port}-es portot. Labirintus aktiválva.")
            kliens_socket.sendall(b"\x03\x01" + random.randbytes(4) + b"\xef\x00\x31")
    except Exception as e:
        logging.error(f"Hiba a hálózati kommunikáció során a(z) {port}-es porton: {e}")
    finally:
        kliens_socket.close()

def ajto_figyelo(port):
    szerver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        szerver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        szerver.bind(("0.0.0.0", port))
        szerver.listen(128)
        while True:
            kliens_socket, cim = szerver.accept()
            threading.Thread(target=kezel_kapu_kommunikacio, args=(kliens_socket, port, cim), daemon=True).start()
    except Exception as e:
        logging.error(f"Nem sikerült elindítani a figyelést a(z) {port}-es porton: {e}")

# ==============================================================================
# HARDVER TELEMETRIA ÉS 2. RÉTEG (AMORF MEMÓRIAVÉDELEM)
# ==============================================================================
def futtat_telemetria_es_amorfizmus():
    global AKTUALIS_POOL_INDEX
    logging.info("TACS_Project: Hardver Telemetria és Amorf Memóriavédelem háttérszál elindult.")
    
    while True:
        try:
            time.sleep(1.0)
            if MEMORIA_POOL[AKTUALIS_POOL_INDEX] is not None:
                puffer = MEMORIA_POOL[AKTUALIS_POOL_INDEX]
                for i in range(len(puffer)):
                    puffer[i] = 0x00
                MEMORIA_POOL[AKTUALIS_POOL_INDEX] = None
                
            AKTUALIS_POOL_INDEX = random.randint(0, 4)
            MEMORIA_POOL[AKTUALIS_POOL_INDEX] = bytearray(TITKOS_TOKEN)
            
        except Exception as e:
            logging.error(f"Hiba a telemetriai vagy amorf memóriakezelési ciklusban: {e}")

# ==============================================================================
# RENDSZER INDÍTÁSA
# ==============================================================================
def indit_teljes_tacs():
    print("=================================================================")
    print("        TACS_Project - INTEGRÁLT BIZTONSÁGI MOTOR v1.2")
    print(" Környezet: Lenovo IdeaPad 100 | Windows 10/11 (Rendszergazda)")
    print("=================================================================")
    print("[*] Rendszer indulása... Ellenőrizd a 'tacs_project_security.log' fájlt.")
    
    threading.Thread(target=futtat_telemetria_es_amorfizmus, daemon=True).start()
    
    for port in PORT_TARTOMANY:
        threading.Thread(target=ajto_figyelo, args=(port,), daemon=True).start()
        
    logging.info("TACS_Project: A teljes védelmi lánc sikeresen inicializálva.")

if __name__ == "__main__":
    # Ha parancssori argumentumként megkapja a watchdog jelzést
    if len(sys.argv) > 1 and "--watchdog" in sys.argv:
        mcafee_orseg_kulon_folyamat()
        sys.exit(0)

    # Háttérfolyamat indítása tiszta listás argumentum-átadással
    subprocess.Popen(sajat_exe + ["--watchdog"], creationflags=subprocess.CREATE_NO_WINDOW)

    indit_teljes_tacs()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] TACS_Project leállítva.")
