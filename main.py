import requests
from bs4 import BeautifulSoup
import time
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# Inisialisasi colorama untuk warna
init(autoreset=True)

# ASCII Art dan Identitas Bot
ASCII_ART = f"""
{Fore.CYAN}██████╗  █████╗ ███╗   ██╗███████╗
{Fore.CYAN}██╔══██╗██╔══██╗████╗  ██║██╔════╝
{Fore.CYAN}██║  ██║███████║██╔██╗ ██║███████╗
{Fore.CYAN}██║  ██║██╔══██║██║╚██╗██║╚════██║
{Fore.CYAN}██████╔╝██║  ██║██║ ╚████║███████║
{Fore.CYAN}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
{Fore.YELLOW}Auto Generate Proxy Bot
{Fore.GREEN}GitHub: https://github.com/qdans
"""

print(ASCII_ART)

# Fungsi untuk menangani sinyal Ctrl+C
def signal_handler(sig, frame):
    print(f"\n{Fore.RED}Bot stopped by user.{Style.RESET_ALL}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Sumber proxy tambahan
PROXY_SOURCES = [
    "https://www.sslproxies.org/",
    "https://free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
]

# Fungsi untuk mengambil proxy dari sumber online
def fetch_proxies():
    proxies = []
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) > 0:
                    ip = cols[0].text
                    port = cols[1].text
                    proxies.append(f"{ip}:{port}")
        except Exception as e:
            print(f"{Fore.RED}Failed to fetch proxies from {url}: {e}{Style.RESET_ALL}")
    return proxies

# Fungsi untuk memeriksa kualitas proxy (latency dan konektivitas)
def check_proxy_quality(proxy):
    try:
        start_time = time.time()
        response = requests.get(
            "http://example.com",
            proxies={"http": proxy, "https": proxy},
            timeout=5
        )
        latency = time.time() - start_time
        if response.status_code == 200 and latency < 2.0:  # Latency maksimal 2 detik
            return True, latency
    except:
        pass
    return False, None

# Fungsi untuk menyimpan proxy ke file
def save_proxy(proxy):
    with open("proxies.txt", "a") as file:
        file.write(proxy + "\n")

# Fungsi utama
def main():
    num_proxies = input(f"{Fore.YELLOW}Enter the number of proxies to generate (leave blank for continuous generation): {Style.RESET_ALL}")
    if num_proxies:
        num_proxies = int(num_proxies)
        count = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            while count < num_proxies:
                proxies = fetch_proxies()
                results = list(executor.map(check_proxy_quality, proxies))
                for proxy, (is_valid, latency) in zip(proxies, results):
                    if is_valid:
                        save_proxy(proxy)
                        count += 1
                        print(f"{Fore.GREEN}Proxy {count} saved: {proxy} (Latency: {latency:.2f}s){Style.RESET_ALL}")
                        if count >= num_proxies:
                            break
                time.sleep(10)  # Tunggu 10 detik sebelum mengambil proxy lagi
    else:
        count = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                proxies = fetch_proxies()
                results = list(executor.map(check_proxy_quality, proxies))
                for proxy, (is_valid, latency) in zip(proxies, results):
                    if is_valid:
                        save_proxy(proxy)
                        count += 1
                        print(f"{Fore.GREEN}Proxy {count} saved: {proxy} (Latency: {latency:.2f}s){Style.RESET_ALL}")
                time.sleep(10)  # Tunggu 10 detik sebelum mengambil proxy lagi

if __name__ == "__main__":
    main()
