import requests
from bs4 import BeautifulSoup
import random

def get_free_proxies():
    url = "https://www.sslproxies.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    proxies = []
    for row in soup.select("table.table tbody tr"):
        tds = row.find_all("td")
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        proxy = f"{ip}:{port}"
        proxies.append(proxy)
    
    return proxies

def check_proxy(proxy):
    test_url = "http://httpbin.org/ip"
    proxies = {"http": f"http://{proxy}", "https": f"https://{proxy}"}
    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} works!")
            return True
    except requests.RequestException:
        pass
    return False

def get_working_proxies():
    proxy_list = get_free_proxies()
    random.shuffle(proxy_list)
    working_proxies = []
    
    for proxy in proxy_list:
        if check_proxy(proxy):
            working_proxies.append(proxy)
    
    with open("working_proxies.txt", "w") as f:
        for proxy in working_proxies:
            f.write(proxy + "\n")
    
    return working_proxies

if __name__ == "__main__":
    working_proxies = get_working_proxies()
    if working_proxies:
        print(f"Saved {len(working_proxies)} working proxies to working_proxies.txt")
    else:
        print("No working proxy found.")
