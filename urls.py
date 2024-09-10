from urllib.parse import urljoin , urlparse
from bs4 import BeautifulSoup
import re
import requests
import argparse
import urllib3
import warnings
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def domain_of_src(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def util_validate(match):
    return "\n" in match or ' ' in match

def find_urls_and_endpoints(domain):
    try:
        # Get the page HTML
        response = requests.get(domain, verify=False, timeout=5)  # Added verify=False to ignore SSL certificate verification
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error: Unable to connect to the domain {domain}")
        print(f"Details: {str(e)}")
        return

    # Define the regex patterns
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
        re.compile(r'fetch\)\([\'"](/[^\'"]+)[\'"]')
    ]

    # Find the URLs and endpoints in the page HTML
    find_and_print_matches(str(soup), domain, domain, regex_patterns)

    # Find the script tags in the soup
    scripts = soup.find_all('script', src=True)

    # For each script tag, fetch its content and find the URLs and endpoints
    for script in scripts:
        src = urljoin(domain, script['src'])
        try:
            response = requests.get(src, verify=False, timeout=5)  # Added verify=False to ignore SSL certificate verification
            find_and_print_matches(response.text, src, domain, regex_patterns)
        except Exception as e:
            print(f"Error: Unable to fetch the script {src}")
            print(f"Details: {str(e)}")

def find_and_print_matches(text, src, domain, regex_patterns):
    # Set to store unique matches
    unique_matches = set()

    # Search for the patterns
    for pattern in regex_patterns:
        matches = re.findall(pattern, text)

        # Filter matches to only keep those that belong to the domain
        filtered_matches = []
        for match in matches:
            # Check if the match is a valid URL or endpoint
            if isinstance(match, tuple):
                match = match[0]

            if util_validate(match):
                continue

            if not (match.startswith('http') or match.startswith('https')):
                if match.startswith('data:'):
                    pass
                elif match.startswith('"data:'):
                    pass
                elif match.startswith("'data:"):
                    pass
                elif match.startswith("'"):
                    match = re.sub(r"^'", "", match)
                    filtered_matches.append(match)
                elif match.startswith('"'):
                    match = re.sub(r'^"', '', match)
                    filtered_matches.append(match)
                elif match.startswith('//'):
                    match = re.sub(r'^//+', '', match)
                    filtered_matches.append(match)
                elif match.startswith('/'):
                    if '.js' in src:
                        filtered_matches.append(domain_of_src(src) + match)
                    else:
                        filtered_matches.append(src + match)
                else:
                    filtered_matches.append(domain + '/' + match) 
            elif match.startswith('http') or match.startswith('https'):
                filtered_matches.append(match)
            else:
                filtered_matches.append(match)

        # Add filtered matches to the set
        unique_matches.update(filtered_matches)

    # Print the unique matches
    for match in unique_matches:
        print(f"{domain} {match}")

def main():
    parser = argparse.ArgumentParser(description="Find all URLs and endpoints from a list of domains via stdin.")
    args = parser.parse_args()

    # Read each domain from stdin and process it
    for line in sys.stdin:
        domain = line.strip()
        if domain:
            find_urls_and_endpoints(domain)

if __name__ == '__main__':
    main()
