import requests
from bs4 import BeautifulSoup
import random
import logging
from fake_useragent import UserAgent
import time
import signal
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ASCII Art for the bot icon
BOT_ICON = r"""
██████╗  █████╗ ███╗   ██╗███████╗
██╔══██╗██╔══██╗████╗  ██║██╔════╝
██║  ██║███████║██╔██╗ ██║███████╗
██║  ██║██╔══██║██║╚██╗██║╚════██║
██████╔╝██║  ██║██║ ╚████║███████║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
"""

GITHUB_LINK = "https://github.com/qdans"

# Proxy sources
PROXY_SOURCES = [
    "https://www.sslproxies.org/",
    "https://www.free-proxy-list.net/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://proxy-daily.com/",
    "https://www.proxy-list.download/HTTP",
    "https://www.proxy-list.download/HTTPS",
    "https://www.proxy-list.download/SOCKS4",
    "https://www.proxy-list.download/SOCKS5",
]

def display_welcome_message():
    print(BOT_ICON)
    print(f"GitHub: {GITHUB_LINK}\n")
    print("Welcome to the Free Proxy Scraper Bot!")
    print("Fetching high-quality free proxies and saving the best ones.\n")

def get_free_proxies():
    ua = UserAgent()
    proxies = []

    for url in PROXY_SOURCES:
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
                    proxies.append(proxy)
        except requests.RequestException as e:
            logging.error(f"Error fetching proxies from {url}: {e}")

    if not proxies:
        logging.warning("No proxies found from any source.")
    return proxies

def check_proxy(proxy):
    test_url = "http://httpbin.org/ip"
    proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    try:
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, headers=headers, timeout=5)
        if response.status_code == 200:
            speed = time.time() - start_time
            logging.info(f"Proxy {proxy} works in {speed:.2f} seconds!")
            return True, speed
    except requests.RequestException:
        return False, float('inf')

    return False, float('inf')

def save_proxies(proxies):
    with open("working_proxies.txt", "w") as f:
        for proxy, speed in proxies:
            f.write(f"{proxy} (Response Time: {speed:.2f}s)\n")
    logging.info(f"Saved {len(proxies)} working proxies to working_proxies.txt")

def get_working_proxies():
    proxy_list = get_free_proxies()

    if not proxy_list:
        logging.error("No proxies retrieved. Exiting...")
        return []

    random.shuffle(proxy_list)
    working_proxies = []

    for proxy in proxy_list:
        is_working, speed = check_proxy(proxy)
        if is_working:
            working_proxies.append((proxy, speed))

    working_proxies.sort(key=lambda x: x[1])
    save_proxies(working_proxies)
    return working_proxies

def signal_handler(sig, frame):
    logging.info("\nCtrl+C detected. Saving current results before exiting...")
    save_proxies(working_proxies)
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    display_welcome_message()
    
    working_proxies = get_working_proxies()

    if working_proxies:
        print("\nTop 10 Fastest Proxies:")
        for proxy, speed in working_proxies[:10]:
            print(f"{proxy} (Response Time: {speed:.2f}s)")
    else:
        print("No working proxy found.")

if __name__ == "__main__":
    main()
