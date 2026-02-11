"""
Quick proof test - 3 URLs x 5 times each (without proxy and with proxy)
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iherb_bypass import CloudflareBypass

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


async def proof_test():
    """Run quick proof test"""
    urls = [
        "https://www.iherb.com/pr/now-foods-omega-3-180-epa-120-dha-200-softgels/424",
        "https://www.iherb.com/pr/california-gold-nutrition-vitamin-d3-125-mcg-5000-iu-360-fish-gelatin-softgels/61865",
        "https://www.iherb.com/pr/now-foods-vitamin-d-3-2000-iu-240-softgels/419"
    ]
    
    results = {
        'without_proxy': {'success': 0, 'failed': 0},
        'with_proxy': {'success': 0, 'failed': 0}
    }
    
    print("\n" + "="*70)
    print(f"PROOF TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test WITHOUT proxy
    print("\n[TEST 1] WITHOUT PROXY - 3 URLs x 5 times = 15 requests")
    print("-"*70)
    bypass = CloudflareBypass()
    try:
        await bypass.setup_browser(use_proxy=False)
        
        for url_idx, url in enumerate(urls, 1):
            url_name = url.split('/')[-1][:30]
            print(f"\n[URL {url_idx}/3] {url_name}")
            
            for req in range(1, 6):
                success, html = await bypass.fetch_page(url)
                if success:
                    results['without_proxy']['success'] += 1
                    print(f"  [{req}/5] [OK] {len(html)} bytes")
                else:
                    results['without_proxy']['failed'] += 1
                    print(f"  [{req}/5] [X] FAILED")
    finally:
        await bypass.close()
    
    await asyncio.sleep(2)
    
    # Test WITH proxy
    print("\n\n[TEST 2] WITH PROXY - 3 URLs x 5 times = 15 requests")
    print("-"*70)
    bypass = CloudflareBypass()
    try:
        await bypass.setup_browser(use_proxy=True, proxy_index=0)
        
        for url_idx, url in enumerate(urls, 1):
            url_name = url.split('/')[-1][:30]
            print(f"\n[URL {url_idx}/3] {url_name}")
            
            for req in range(1, 6):
                success, html = await bypass.fetch_page(url)
                if success:
                    results['with_proxy']['success'] += 1
                    print(f"  [{req}/5] [OK] {len(html)} bytes")
                else:
                    results['with_proxy']['failed'] += 1
                    print(f"  [{req}/5] [X] FAILED")
    finally:
        await bypass.close()
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    
    wp = results['without_proxy']
    total_wp = wp['success'] + wp['failed']
    print(f"\nWITHOUT PROXY:")
    print(f"  Success: {wp['success']}/{total_wp} ({wp['success']/total_wp*100:.1f}%)")
    print(f"  Failed:  {wp['failed']}/{total_wp}")
    
    p = results['with_proxy']
    total_p = p['success'] + p['failed']
    print(f"\nWITH PROXY:")
    print(f"  Success: {p['success']}/{total_p} ({p['success']/total_p*100:.1f}%)")
    print(f"  Failed:  {p['failed']}/{total_p}")
    
    print("\n" + "="*70)
    
    # Save to file
    with open('proof_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"PROOF TEST RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")
        f.write(f"WITHOUT PROXY: {wp['success']}/{total_wp} success ({wp['success']/total_wp*100:.1f}%)\n")
        f.write(f"WITH PROXY: {p['success']}/{total_p} success ({p['success']/total_p*100:.1f}%)\n")
    
    print("\nResults saved to: proof_results.txt")


if __name__ == "__main__":
    asyncio.run(proof_test())
