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
    working_proxies = set()
    checked_proxies = set()

    try:
        with open("working_proxies.txt", "r") as f:
            existing_proxies = {line.split()[0] for line in f.readlines()}
    except FileNotFoundError:
        existing_proxies = set()
    
    while max_proxies_to_check is None or len(working_proxies) < max_proxies_to_check:
        proxy_list = get_free_proxies()
        random.shuffle(proxy_list)
        
        for proxy in proxy_list:
            if proxy in checked_proxies or proxy in existing_proxies:
                continue
            
            checked_proxies.add(proxy)
            is_working, speed = check_proxy(proxy)
            if is_working:
                working_proxies.add((proxy, speed))
                existing_proxies.add(proxy)
                
                with open("working_proxies.txt", "a") as f:
                    f.write(f"{proxy} (Response Time: {speed:.2f}s)
")
                
                if max_proxies_to_check and len(working_proxies) >= max_proxies_to_check:
                    break
    
    logging.info(f"Collected {len(working_proxies)} working proxies.")
    return sorted(working_proxies, key=lambda x: x[1])

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

    user_input = input("Enter the number of proxies to generate (or press Enter for unlimited): ")
    max_proxies_to_check = int(user_input) if user_input.strip().isdigit() else None

    working_proxies = get_working_proxies(max_proxies_to_check)

    if working_proxies:
        print("\nTop 10 Fastest Proxies:")
        for proxy, speed in working_proxies[:10]:
            print(f"{proxy} (Response Time: {speed:.2f}s)")
    else:
        print("No working proxy found.")

if __name__ == "__main__":
    main()
