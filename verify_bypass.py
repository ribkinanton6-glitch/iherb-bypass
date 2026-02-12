"""
FINAL VERIFICATION SCRIPT
Demonstrates Cloudflare Bypass using Session Persistence
"""
import asyncio
import json
import os
import sys

# Add current directory to path so we can import iherb_bypass
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from iherb_bypass import CloudflareBypass

async def main():
    print("=" * 60)
    print("🚀 FINAL BYPASS VERIFICATION TEST")
    print("=" * 60)
    
    # 1. CLEANUP: Remove old cookies to start fresh
    if os.path.exists('cookies.json'):
        os.remove('cookies.json')
        print("[*] Cleaned up old cookies.json (Starting fresh)")
    
    
    # ---------------------------------------------------------
    # STEP 1: ESTABLISH SESSION (Simulate good IP/No Proxy)
    # ---------------------------------------------------------
    print("\n[Step 1] Establishing clean session (Direct Connection)...")
    bypass = CloudflareBypass()
    # Ensure usage of direct connection for this step
    await bypass.setup_browser(use_proxy=False)
    
    url = "https://www.iherb.com/pr/now-foods-omega-3-180-epa-120-dha-200-softgels/424"
    success, html = await bypass.fetch_page(url)
    
    if success:
        print(f"  ✅ Success! Page loaded ({len(html)} bytes)")
        if os.path.exists('cookies.json'):
            print("  ✅ COOKIES SAVED! Session persisted to 'cookies.json'")
        else:
            print("  ❌ Error: Cookies were not saved!")
            return
    else:
        print(f"  ❌ Failed to establish initial session: {html}")
        return
        
    await bypass.close()
    
    
    # ---------------------------------------------------------
    # STEP 2: BYPASS WITH PROXY (Using Saved Cookies)
    # ---------------------------------------------------------
    print("\n[Step 2] Testing Asocks Proxy (Using Persisted Session)...")
    print("  [*] Connecting via 93.190.141.105:443...")
    
    # Initialize new instance (simulates a restart)
    bypass_proxy = CloudflareBypass()
    # Enable proxy!
    await bypass_proxy.setup_browser(use_proxy=True)
    
    success_proxy, html_proxy = await bypass_proxy.fetch_page(url)
    
    if success_proxy:
        print(f"  ✅ SUCCESS! Proxy bypassed Cloudflare! 🚀")
        print(f"  📦 Content received: {len(html_proxy)} bytes")
        title_idx = html_proxy.find('<title>')
        if title_idx != -1:
            title_end = html_proxy.find('</title>', title_idx)
            print(f"  📄 Page Title: {html_proxy[title_idx:title_end+8]}")
            
        print("\n🎉 CONCLUSION: Bypass Strategy Works!")
    else:
        print(f"  ❌ Failed with proxy: {html_proxy}")
        
    await bypass_proxy.close()

if __name__ == "__main__":
    asyncio.run(main())
