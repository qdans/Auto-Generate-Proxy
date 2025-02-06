import requests
from bs4 import BeautifulSoup
import random
import logging
from fake_useragent import UserAgent
import time
import os
import signal

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

# Function to handle Ctrl+C
def signal_handler(sig, frame):
    print("\nExiting bot...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def display_welcome_message():
    print(BOT_ICON)
    print(f"GitHub: {GITHUB_LINK}\n")
    print("Welcome to the Free Proxy Scraper Bot!")
    print("This bot will help you find high-quality free proxies from multiple sources.")
    print("It automatically fetches and checks proxies without user input.\n")

def get_free_proxies():
    sources = [
        "https://www.sslproxies.org/",
        "https://www.free-proxy-list.net/",
        "https://www.us-proxy.org/",
        "https://www.socks-proxy.net/",
        "https://www.proxy-list.download/HTTPS",
        "https://www.proxy-list.download/HTTP",
        "https://www.proxy-list.download/SOCKS4",
        "https://www.proxy-list.download/SOCKS5",
        "https://www.proxyscrape.com/free-proxy-list",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
    ]
    ua = UserAgent()
    proxies = []

    for url in sources:
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
    test_urls = [
        "http://httpbin.org/ip",
        "https://www.google.com",
        "https://www.amazon.com"
    ]
    proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    for url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(url, proxies=proxies, headers=headers, timeout=5)
            if response.status_code == 200:
                speed = time.time() - start_time
                logging.info(f"Proxy {proxy} works with {url} in {speed:.2f} seconds!")
                return True, speed
        except requests.RequestException as e:
            logging.debug(f"Proxy {proxy} failed with {url}: {e}")
            continue

    return False, float('inf')

def get_working_proxies():
    # Clear previous run history
    if os.path.exists("working_proxies.txt"):
        os.remove("working_proxies.txt")

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

    # Sort proxies by speed (fastest first)
    working_proxies.sort(key=lambda x: x[1])

    if working_proxies:
        with open("working_proxies.txt", "w") as f:
            for proxy, speed in working_proxies:
                f.write(f"{proxy} (Response Time: {speed:.2f}s)\n")
        logging.info(f"Saved {len(working_proxies)} working proxies to working_proxies.txt")
    else:
        logging.warning("No working proxy found.")

    return working_proxies

def main():
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
