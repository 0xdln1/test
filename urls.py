#!/usr/bin/env python3
"""
Enhanced URL Extractor - Extracts all URLs from a given URL
Optimized for cache poisoning detection (includes all static assets)
Output format: JSON lines for easy parsing
"""
import sys
import re
import json
from urllib.parse import urljoin, urlparse
from collections import OrderedDict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Install dependencies: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)

def extract_urls(source_url, timeout=10):
    """Extract all URLs from a given URL"""
    urls = OrderedDict()  # Preserve order, auto-deduplicate
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(source_url, headers=headers, timeout=timeout, verify=False)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract from common tags
        # <script src="...">
        for tag in soup.find_all('script', src=True):
            url = urljoin(source_url, tag['src'])
            urls[url] = 'script'
        
        # <link href="..."> (CSS, icons, etc.)
        for tag in soup.find_all('link', href=True):
            url = urljoin(source_url, tag['href'])
            urls[url] = 'link'
        
        # <img src="...">
        for tag in soup.find_all('img', src=True):
            url = urljoin(source_url, tag['src'])
            urls[url] = 'img'
        
        # <a href="...">
        for tag in soup.find_all('a', href=True):
            url = urljoin(source_url, tag['href'])
            # Skip anchors and javascript
            if not url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                urls[url] = 'link'
        
        # <iframe src="...">
        for tag in soup.find_all('iframe', src=True):
            url = urljoin(source_url, tag['src'])
            urls[url] = 'iframe'
        
        # <video src="..."> and <source src="...">
        for tag in soup.find_all(['video', 'source'], src=True):
            url = urljoin(source_url, tag['src'])
            urls[url] = 'media'
        
        # Extract from inline scripts and styles (regex)
        # Look for URLs in quotes
        url_pattern = r'["\']((https?:)?//[^"\']+)["\']'
        for match in re.finditer(url_pattern, response.text):
            url = match.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            if url.startswith('http'):
                urls[url] = 'inline'
        
        # Extract from CSS (background-image, etc.)
        css_url_pattern = r'url\(["\']?([^"\')]+)["\']?\)'
        for match in re.finditer(css_url_pattern, response.text):
            url = urljoin(source_url, match.group(1))
            urls[url] = 'css'
        
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "source": source_url,
            "error": str(e),
            "extracted": []
        }), file=sys.stderr)
        return []
    except Exception as e:
        print(json.dumps({
            "source": source_url,
            "error": f"Parse error: {str(e)}",
            "extracted": []
        }), file=sys.stderr)
        return []
    
    return urls

def main():
    """Process URLs from stdin"""
    if len(sys.argv) > 1:
        # Single URL mode
        source_url = sys.argv[1]
        urls = extract_urls(source_url)
        
        result = {
            "source": source_url,
            "extracted_count": len(urls),
            "urls": [{"url": url, "type": typ} for url, typ in urls.items()]
        }
        print(json.dumps(result))
    else:
        # Batch mode from stdin
        for line in sys.stdin:
            source_url = line.strip()
            if not source_url:
                continue
            
            urls = extract_urls(source_url)
            
            result = {
                "source": source_url,
                "extracted_count": len(urls),
                "urls": [{"url": url, "type": typ} for url, typ in urls.items()]
            }
            print(json.dumps(result))
            sys.stdout.flush()

if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
