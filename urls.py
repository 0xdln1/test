from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import sys
import requests
import argparse
import urllib3
import warnings

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def util_validate(match):
    return "\n" in match or ' ' in match

def find_urls_and_endpoints(domain):
    global_matches = set()

    try:
        response = requests.get(domain, verify=False, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error: Unable to connect to the domain {domain}")
        print(f"Details: {str(e)}")
        return

    regex_patterns = [
        re.compile(r'src="([^"]*)"'),
        re.compile(r'url\(([^)]+)\)'),
        re.compile(r'xml:"([^"\s]*)"', re.IGNORECASE),
        re.compile(r'<script[^>]*src="([^"]*)"[^>]*>', re.IGNORECASE),
        re.compile(r'(https:\/\/[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\/[a-zA-Z0-9-._%&?=\/+@#:]+)*)'),
        re.compile(r'url\s*=\s*`(.*?)`'),
        re.compile(r'href="([^"]*)"'),
        re.compile(r'fetch\(\s*[\'"]([^\'"]+)[\'"]'),
        re.compile(r'open\(\s*[\'"][A-Z]+[\'"],\s*[\'"]([^\'"]+)[\'"]'),
        re.compile(r'\$\.ajax\(\s*\{\s*url:\s*[\'"]([^\'"]+)[\'"]'),
        re.compile(r'axios\.\w+\(\s*[\'"]([^\'"]+)[\'"]'),
        re.compile(r'url:"([^"]+)'),
        re.compile(r'fetch\)\([\'"](/[^\'"]+)[\'"]'),
        re.compile(r'\.src\s*=\s*[\'"]([^\'"]+)[\'"]'),
        re.compile(r'["\'](\/[^"\']+\.js)["\']')
    ]

    find_and_print_matches(str(soup), domain, domain, regex_patterns, global_matches)

    scripts = soup.find_all('script', src=True)
    for script in scripts:
        src = urljoin(domain, script['src'])
        try:
            response = requests.get(src, verify=False, timeout=5)
            find_and_print_matches(response.text, src, domain, regex_patterns, global_matches)
        except Exception as e:
            print(f"Error: Unable to fetch the script {src}")
            print(f"Details: {str(e)}")

    inline_scripts = soup.find_all('script', src=False)
    for script in inline_scripts:
        script_content = script.string
        if script_content:
            find_and_print_matches(script_content, domain, domain, regex_patterns, global_matches)

def find_and_print_matches(text, src, domain, regex_patterns, global_set):
    for pattern in regex_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]

            if util_validate(match):
                continue

            match = match.strip('\'"')

            if match.startswith('data:') or match.startswith('/data:'):
                continue

            if match.startswith('//'):
                match = match[2:]  # Remove the "//" prefix, don't convert to full URL
            elif not match.startswith(('http://', 'https://')):
                match = urljoin(domain, match)

            if match not in global_set:
                global_set.add(match)
                print(f"{domain} {match}")

def main():
    parser = argparse.ArgumentParser(description="Find all URLs and endpoints in a domain.")
    parser.add_argument('domain', type=str, nargs='?', help='The domain to search.')
    args = parser.parse_args()

    if args.domain:
        find_urls_and_endpoints(args.domain)
    else:
        for line in sys.stdin:
            domain = line.strip()
            if domain:
                find_urls_and_endpoints(domain)

if __name__ == '__main__':
    main()
