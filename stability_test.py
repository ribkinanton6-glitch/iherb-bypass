"""
Stability Test Runner
Tests the iHerb bypass script with 5 URLs × 30 requests each
"""
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from iherb_bypass import CloudflareBypass

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class StabilityTest:
    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.test_urls = self.config['test_urls']
        self.results = {
            'without_proxy': {'success': 0, 'failed': 0, 'errors': []},
            'with_proxy': {'success': 0, 'failed': 0, 'errors': []}
        }
    
    async def run_test(self, use_proxy: bool = False, requests_per_url: int = 30):
        """Run stability test"""
        test_type = "WITH PROXY" if use_proxy else "WITHOUT PROXY"
        print(f"\n{'='*60}")
        print(f"Starting test: {test_type}")
        print(f"URLs: {len(self.test_urls)}")
        print(f"Requests per URL: {requests_per_url}")
        print(f"Total requests: {len(self.test_urls) * requests_per_url}")
        print(f"{'='*60}\n")
        
        bypass = CloudflareBypass()
        await bypass.setup_browser(use_proxy=use_proxy)
        
        start_time = time.time()
        
        for url_idx, url in enumerate(self.test_urls, 1):
            print(f"\n[URL {url_idx}/{len(self.test_urls)}] {url}")
            print(f"{'─'*60}")
            
            url_success = 0
            url_failed = 0
            
            for req_num in range(1, requests_per_url + 1):
                try:
                    success, html = await bypass.fetch_page(url)
                    
                    if success:
                        url_success += 1
                        print(f"  [{req_num:2d}/30] [OK] Success ({len(html)} bytes)")
                    else:
                        url_failed += 1
                        print(f"  [{req_num:2d}/30] [X] Failed: {html[:50]}")
                        
                        # Save failed response for debugging
                        self._save_failed_response(url, req_num, html, use_proxy)
                        
                        if use_proxy:
                            self.results['with_proxy']['errors'].append({
                                'url': url,
                                'request': req_num,
                                'error': html[:200]
                            })
                        else:
                            self.results['without_proxy']['errors'].append({
                                'url': url,
                                'request': req_num,
                                'error': html[:200]
                            })
                
                except Exception as e:
                    url_failed += 1
                    error_msg = str(e)[:100]
                    print(f"  [{req_num:2d}/30] [!] Exception: {error_msg}")
                    
                    if use_proxy:
                        self.results['with_proxy']['errors'].append({
                            'url': url,
                            'request': req_num,
                            'error': error_msg
                        })
                    else:
                        self.results['without_proxy']['errors'].append({
                            'url': url,
                            'request': req_num,
                            'error': error_msg
                        })
            
            # Update totals
            if use_proxy:
                self.results['with_proxy']['success'] += url_success
                self.results['with_proxy']['failed'] += url_failed
            else:
                self.results['without_proxy']['success'] += url_success
                self.results['without_proxy']['failed'] += url_failed
            
            print(f"\nURL Summary: {url_success}/30 successful ({url_success/30*100:.1f}%)")
        
        await bypass.close()
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Test completed in {elapsed:.1f}s")
        print(f"{'='*60}\n")
    
    def _save_failed_response(self, url: str, req_num: int, html: str, use_proxy: bool):
        """Save failed HTML response for debugging"""
        debug_dir = Path("debug_responses")
        debug_dir.mkdir(exist_ok=True)
        
        filename = f"{'proxy' if use_proxy else 'no_proxy'}_url{url.split('/')[-1]}_req{req_num}.html"
        filepath = debug_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def print_summary(self):
        """Print final test summary"""
        print(f"\n{'='*60}")
        print("FINAL RESULTS")
        print(f"{'='*60}\n")
        
        # Without proxy
        wp = self.results['without_proxy']
        total_wp = wp['success'] + wp['failed']
        if total_wp > 0:
            print(f"WITHOUT PROXY:")
            print(f"  [OK] Success: {wp['success']}/{total_wp} ({wp['success']/total_wp*100:.1f}%)")
            print(f"  [X] Failed:  {wp['failed']}/{total_wp} ({wp['failed']/total_wp*100:.1f}%)")
            if wp['errors']:
                print(f"  First error: {wp['errors'][0]['error'][:80]}")
        
        print()
        
        # With proxy
        p = self.results['with_proxy']
        total_p = p['success'] + p['failed']
        if total_p > 0:
            print(f"WITH PROXY:")
            print(f"  [OK] Success: {p['success']}/{total_p} ({p['success']/total_p*100:.1f}%)")
            print(f"  [X] Failed:  {p['failed']}/{total_p} ({p['failed']/total_p*100:.1f}%)")
            if p['errors']:
                print(f"  First error: {p['errors'][0]['error'][:80]}")
        
        print(f"\n{'='*60}\n")
        
        # Save results to JSON
        with open(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(self.results, f, indent=2)


async def main():
    """Run full stability test"""
    tester = StabilityTest()
    
    # Test 1: Without proxy
    await tester.run_test(use_proxy=False, requests_per_url=30)
    
    # Test 2: With proxy
    await tester.run_test(use_proxy=True, requests_per_url=30)
    
    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
