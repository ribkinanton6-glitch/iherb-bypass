"""
Check Proxy IP Script
Verifies that the script is actually using the proxy for connections.
"""
import asyncio
import json
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from iherb_bypass import CloudflareBypass

async def main():
    print("=" * 60)
    print("🔎 PROXY IP VERIFICATION")
    print("=" * 60)
    
    # Check Config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    proxies = config.get('proxies', [])
    if not proxies:
        print("[!] No proxies found in config.json")
        return

    proxy_info = proxies[0]
    print(f"Configured Proxy: {proxy_info['host']}:{proxy_info['port']}")
    
    bypass = CloudflareBypass()
    
    try:
        # 1. Check IP WITHOUT Proxy
        print("\n[1] Checking Direct IP (No Proxy)...")
        await bypass.setup_browser(use_proxy=False)
        # Verify using a simple IP echo service
        success, content = await bypass.fetch_page("https://api.ipify.org?format=json")
        if success:
            try:
                ip_data = json.loads(content.replace('<html><head></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '').replace('</pre></body></html>', '')) # Clean up if Playwright wraps it
                # Playwright .content() returns full HTML, ipify returns plain JSON usually, but browser might wrap it.
                # Let's verify text content directly
                page = bypass.context.pages[0] 
                # Better to get text directly
                text = await page.locator('body').text_content()
                print(f"    Current IP: {text}")
            except:
                 print(f"    Raw content: {content[:100]}")
        else:
            print("    [!] Failed to get IP")
            
        await bypass.close()
        
        # 2. Check IP WITH Proxy
        print("\n[2] Checking Proxy IP via 93.190.141.105...")
        # Re-init
        bypass = CloudflareBypass()
        await bypass.setup_browser(use_proxy=True)
        
        # Use httpbin which is less likely to be blocked by CF than ipify
        success, content = await bypass.fetch_page("http://httpbin.org/ip")
        
        if success:
            try:
                 # httpbin returns { "origin": "1.2.3.4" }
                 # Playwright might wrap in html, so find the JSON part
                 import re
                 json_match = re.search(r'\{.*\}', content, re.DOTALL)
                 if json_match:
                     ip_data = json.loads(json_match.group(0))
                     print(f"    Proxy IP (from httpbin): {ip_data.get('origin')}")
                 else:
                     # Fallback to text content
                     page = bypass.context.pages[0] 
                     text = await page.locator('body').text_content()
                     print(f"    Proxy IP (text): {text[:50]}")
            except Exception as e:
                 print(f"    [!] Error parsing IP: {e}")
                 print(f"    Raw content: {content[:100]}")
        else:
            print("    [X] Failed to get Proxy IP (Might be blocked or slow)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bypass.close()

if __name__ == "__main__":
    asyncio.run(main())
