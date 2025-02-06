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
    logging.FileHandler("proxy_scraper.log"),
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

# Additional Proxy Sources
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
            logging.info(f"Proxy {proxy} is working! Response time: {speed:.2f}s")
            return True, speed
    except requests.exceptions.Timeout:
        logging.warning(f"Proxy {proxy} timed out.")
    except requests.exceptions.SSLError:
        logging.warning(f"Proxy {proxy} encountered SSL error.")
    except requests.exceptions.RequestException as e:
        logging.debug(f"Proxy {proxy} failed: {e}")

    return False, float('inf')

def get_working_proxies(max_proxies_to_check):
    proxy_list = get_free_proxies()

    if not proxy_list:
        logging.error("No proxies retrieved. Exiting...")
        return []

    random.shuffle(proxy_list)
    working_proxies = []

    for proxy in proxy_list[:max_proxies_to_check]:
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

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Exiting gracefully...")
    logging.info("User terminated the program with Ctrl+C.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    print(BOT_ASCII_ART)
    print("Welcome to the Free Proxy Scraper Bot!")
    print("Press Ctrl+C to stop the bot at any time.")
    print("This tool fetches free proxies, tests them, and saves the best ones in 'working_proxies.txt'.")

    try:
        max_proxies_to_check = int(input("Enter the number of proxies to test (e.g., 50): "))
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    working_proxies = get_working_proxies(max_proxies_to_check)

    if working_proxies:
        print("\nTop 10 Fastest Proxies:")
        for proxy, speed in working_proxies[:10]:
            print(f"{proxy} (Response Time: {speed:.2f}s)")
    else:
        print("No working proxy found.")

if __name__ == "__main__":
    main()
