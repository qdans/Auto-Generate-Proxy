import requests
from bs4 import BeautifulSoup
import random
import logging
from fake_useragent import UserAgent
import time
import signal
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("main.log", encoding='utf-8'),
    logging.StreamHandler()
])

# ASCII Art
BOT_ASCII_ART = """
██████╗  █████╗ ███╗   ██╗███████╗
██╔══██╗██╔══██╗████╗  ██║██╔════╝
██║  ██║███████║██╔██╗ ██║███████╗
██║  ██║██╔══██║██║╚██╗██║╚════██║
██████╔╝██║  ██║██║ ╚████║███████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
"""

# Sumber proxy tambahan
SOURCES = [
    "https://www.sslproxies.org/",
    "https://www.free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://proxy-daily.com/",
    "https://www.proxy-list.download/HTTP",
    "https://www.proxy-list.download/HTTPS",
    "https://www.proxy-list.download/SOCKS4",
    "https://www.proxy-list.download/SOCKS5"
]

def get_free_proxies():
    ua = UserAgent()
    proxies = set()

    for url in SOURCES:
        try:
            headers = {"User-Agent": ua.random}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch proxy list from {url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for row in soup.select("table.table tbody tr"):
                tds = row.find_all("td")
                if len(tds) >= 2:
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    proxy = f"{ip}:{port}"
                    proxies.add(proxy)

        except requests.RequestException as e:
            logging.error(f"Error fetching proxies from {url}: {e}")

    if not proxies:
        logging.warning("No proxies found from any source.")
    return list(proxies)

def main():
    print(BOT_ASCII_ART)
    print("Welcome to the Free Proxy Scraper Bot!")
    print("Press Ctrl+C to stop the bot at any time.")
    
    # Meminta jumlah proxy yang ingin digenerate dari pengguna
    while True:
        try:
            user_input = input("Enter the number of proxies you want to generate (leave blank to run indefinitely): ").strip()
            if user_input == "":
                max_proxies = float('inf')  # Loop tanpa henti
            else:
                max_proxies = int(user_input)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    print(f"Generating up to {max_proxies} proxies...")
    
    proxies = get_free_proxies()
    print(f"Total proxies found: {len(proxies)}")

if __name__ == "__main__":
    main()
