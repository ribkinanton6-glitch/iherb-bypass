"""
Extended test script to verify:
1. Proxy connection works
2. Multiple URLs can be fetched
3. Cloudflare detection works
4. Error handling is robust
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iherb_bypass import CloudflareBypass

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


async def test_basic():
    """Test 1: Basic fetch without proxy"""
    print("\n" + "="*60)
    print("TEST 1: Basic fetch (no proxy)")
    print("="*60)
    
    bypass = CloudflareBypass()
    try:
        await bypass.setup_browser(use_proxy=False)
        url = "https://www.iherb.com/pr/now-foods-omega-3-180-epa-120-dha-200-softgels/424"
        success, html = await bypass.fetch_page(url)
        
        if success:
            print(f"[OK] Success! Got {len(html)} bytes")
            # Check for iHerb content
            if 'iherb' in html.lower() and 'product' in html.lower():
                print("[OK] Page contains iHerb product content")
            else:
                print("[X] WARNING: Page might be Cloudflare challenge")
        else:
            print(f"[X] Failed: {html[:100]}")
    finally:
        await bypass.close()


async def test_proxy():
    """Test 2: Fetch with proxy"""
    print("\n" + "="*60)
    print("TEST 2: Fetch with proxy")
    print("="*60)
    
    bypass = CloudflareBypass()
    try:
        await bypass.setup_browser(use_proxy=True, proxy_index=0)
        url = "https://www.iherb.com/pr/california-gold-nutrition-vitamin-d3-125-mcg-5000-iu-360-fish-gelatin-softgels/61865"
        success, html = await bypass.fetch_page(url)
        
        if success:
            print(f"[OK] Success with proxy! Got {len(html)} bytes")
        else:
            print(f"[X] Failed with proxy: {html[:100]}")
    finally:
        await bypass.close()


async def test_multiple_urls():
    """Test 3: Fetch multiple URLs sequentially"""
    print("\n" + "="*60)
    print("TEST 3: Multiple URLs (3 URLs)")
    print("="*60)
    
    urls = [
        "https://www.iherb.com/pr/now-foods-omega-3-180-epa-120-dha-200-softgels/424",
        "https://www.iherb.com/pr/california-gold-nutrition-vitamin-d3-125-mcg-5000-iu-360-fish-gelatin-softgels/61865",
        "https://www.iherb.com/pr/now-foods-vitamin-d-3-2000-iu-240-softgels/419"
    ]
    
    bypass = CloudflareBypass()
    try:
        await bypass.setup_browser(use_proxy=False)
        
        success_count = 0
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/3] Fetching: {url.split('/')[-1]}")
            success, html = await bypass.fetch_page(url)
            if success:
                success_count += 1
                print(f"  [OK] Success ({len(html)} bytes)")
            else:
                print(f"  [X] Failed: {html[:50]}")
        
        print(f"\nResult: {success_count}/3 successful ({success_count/3*100:.0f}%)")
    finally:
        await bypass.close()


async def test_cloudflare_detection():
    """Test 4: Cloudflare detection logic"""
    print("\n" + "="*60)
    print("TEST 4: Cloudflare detection logic")
    print("="*60)
    
    bypass = CloudflareBypass()
    
    # Test with fake Cloudflare page
    fake_cf_html = "<html><body>Checking your browser before accessing</body></html>"
    is_cf = bypass._is_cloudflare_challenge(fake_cf_html)
    print(f"Fake Cloudflare page detected: {is_cf} (should be True)")
    
    # Test with fake iHerb page
    fake_iherb_html = "<html><body><h1>iHerb Product</h1><button>Add to Cart</button></body></html>"
    is_cf = bypass._is_cloudflare_challenge(fake_iherb_html)
    print(f"Fake iHerb page detected as CF: {is_cf} (should be False)")
    
    if is_cf:
        print("[X] WARNING: Detection logic might be too strict")
    else:
        print("[OK] Detection logic works correctly")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("EXTENDED TEST SUITE")
    print("="*60)
    
    try:
        await test_basic()
        await asyncio.sleep(2)
        
        await test_proxy()
        await asyncio.sleep(2)
        
        await test_multiple_urls()
        await asyncio.sleep(2)
        
        await test_cloudflare_detection()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"\n[X] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
