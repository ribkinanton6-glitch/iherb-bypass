"""
iHerb Cloudflare Bypass Script
Uses Playwright + stealth techniques to bypass Cloudflare protection
"""
import asyncio
import json
import random
import time
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# 2Captcha integration
try:
    from twocaptcha import TwoCaptcha
    CAPTCHA_AVAILABLE = True
except ImportError:
    CAPTCHA_AVAILABLE = False
    print("[!] 2captcha-python not installed. Captcha solving disabled.")

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


class CloudflareBypass:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.stealth = self.config['stealth_settings']
        self.browser: Browser = None
        self.context: BrowserContext = None
        
        # Initialize 2Captcha solver if API key provided
        self.captcha_solver = None
        if CAPTCHA_AVAILABLE and self.config.get('captcha_api_key'):
            self.captcha_solver = TwoCaptcha(self.config['captcha_api_key'])
            print("[+] 2Captcha solver initialized")
    
    async def setup_browser(self, use_proxy: bool = False, proxy_index: int = 0):
        """Initialize browser with stealth settings"""
        playwright = await async_playwright().start()
        
        # Browser args for stealth
        args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-infobars',
            '--window-position=0,0',
            '--ignore-certificate-errors',
            '--ignore-certificate-errors-spki-list',
            '--disable-gpu',
        ]
        
        # Launch browser
        self.browser = await playwright.chromium.launch(
            headless=False,  # Cloudflare detects headless
            args=args
        )
        
        # Context options
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': 'en-US',
            'timezone_id': 'America/New_York',
            'permissions': ['geolocation'],
            'geolocation': {'latitude': 40.7128, 'longitude': -74.0060},
            'color_scheme': 'light',
            'java_script_enabled': True,
        }
        
        # Add proxy if requested
        if use_proxy and self.config['proxies']:
            proxy = self.config['proxies'][proxy_index % len(self.config['proxies'])]
            context_options['proxy'] = {
                'server': f"{proxy['type']}://{proxy['host']}:{proxy['port']}",
                'username': proxy['username'],
                'password': proxy['password']
            }
            print(f"Using proxy: {proxy['host']}:{proxy['port']}")
        
        self.context = await self.browser.new_context(**context_options)
        
        # Apply CDP patches to hide automation
        # Apply CDP patches to hide automation
        await self._apply_stealth_patches()
        
        # Load tokens if available
        await self._load_cookies(self.context)
        
        return self.context
    
    async def _apply_stealth_patches(self):
        """Apply Chrome DevTools Protocol patches to hide automation"""
        # This will be applied to all pages in the context
        await self.context.add_init_script("""
            // Overwrite the `navigator.webdriver` property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Overwrite the `navigator.plugins` to look real
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite the `navigator.languages` to look real
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Remove Playwright-specific properties
            delete navigator.__proto__.webdriver;
            
            // Mock chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Randomize canvas fingerprint slightly
            const getImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(...args) {
                const imageData = getImageData.apply(this, args);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 3) - 1;
                }
                return imageData;
            };
            
            // Mock WebGL vendor
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
        """)
    
    async def fetch_page(self, url: str, retry_count: int = 0) -> tuple[bool, str]:
        """
        Fetch a page and return (success, html_content)
        success = True if we got real content (not Cloudflare challenge)
        """
        if retry_count >= self.stealth['max_retries']:
            return False, "Max retries exceeded"
        
        page = await self.context.new_page()
        
        try:
            # Random delay before request (human-like)
            await asyncio.sleep(random.uniform(
                self.stealth['min_delay_ms'] / 1000,
                self.stealth['max_delay_ms'] / 1000
            ))
            
            # Navigate to page (use domcontentloaded, NOT networkidle!)
            # networkidle never completes on Cloudflare pages (they keep polling)
            response = await page.goto(url, wait_until='domcontentloaded', timeout=self.stealth['timeout_ms'])
            
            # Wait for Cloudflare JS challenge to auto-resolve (up to 15 seconds)
            await asyncio.sleep(5)
            
            # Get page content
            html = await page.content()
            
            # Check if we got Cloudflare challenge
            if self._is_cloudflare_challenge(html):
                print(f"  [X] Cloudflare challenge detected (attempt {retry_count + 1})")
                
                # Wait longer for JS challenge to auto-solve
                # Wait longer for JS challenge to auto-solve with human interaction
                print("  [~] Waiting for Cloudflare JS challenge to resolve (with mouse moves)...")
                for i in range(4):
                    # Simulate human behavior
                    await self._humanize_mouse(page)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    html = await page.content()
                    if not self._is_cloudflare_challenge(html):
                        print(f"  [✓] Challenge resolved after interactive wait!")
                        await self._save_cookies(self.context)
                        await page.close()
                        return True, html
                
                # Still blocked? Try 2Captcha if available
                if self.captcha_solver:
                    print("  [~] Attempting to solve with 2Captcha...")
                    solved = await self._solve_cloudflare_turnstile(page, url)
                    if solved:
                        print("  [✓] Captcha solved! Reloading page...")
                        await asyncio.sleep(5)
                        html = await page.content()
                        
                        # Check if we got through
                        if not self._is_cloudflare_challenge(html):
                            await self._save_cookies(self.context)
                            await page.close()
                            return True, html
                        else:
                            print("  [X] Still blocked after captcha solve")
                
                await page.close()
                # Retry with exponential backoff
                await asyncio.sleep(2 ** retry_count)
                return await self.fetch_page(url, retry_count + 1)
            
            # Success!
            await self._save_cookies(self.context)
            await page.close()
            return True, html
            
        except Exception as e:
            print(f"  [!] Error: {str(e)[:100]}")
            await page.close()
            return False, str(e)
            
    async def _humanize_mouse(self, page: Page):
        """Simulate human-like mouse movements to pass Cloudflare JS challenge"""
        try:
            # Move mouse randomly
            for _ in range(random.randint(3, 7)):
                x = random.randint(100, 1000)
                y = random.randint(100, 700)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.5))
        except:
            pass

    async def _save_cookies(self, context: BrowserContext):
        """Save cookies to file for persistence"""
        try:
            cookies = await context.cookies()
            with open('cookies.json', 'w') as f:
                json.dump(cookies, f)
            # print("  [~] Cookies saved")
        except:
            pass
            
    async def _load_cookies(self, context: BrowserContext):
        """Load cookies from file if exists"""
        try:
            if os.path.exists('cookies.json'):
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                print("  [+] Loaded persisted session cookies")
        except:
            pass
    
    def _is_cloudflare_challenge(self, html: str) -> bool:
        """Check if the HTML is a Cloudflare challenge page"""
        html_lower = html.lower()
        
        # 1. If page is large (>100KB) and has iHerb content = real page, NOT challenge
        # Real iHerb pages are 1-2MB+, Cloudflare challenges are ~28KB
        if len(html) > 100000:
            return False
        
        # 2. Check for Cloudflare challenge markers
        cloudflare_markers = [
            'checking your browser',
            'just a moment',
            'enable javascript and cookies to continue',
            'cf-browser-verification',
            'cf_chl_opt',
            'challenge-platform',
            'verifying you are human',
        ]
        
        for marker in cloudflare_markers:
            if marker in html_lower:
                return True
        
        # 3. If page is very small, likely blocked/error
        if len(html) < 5000:
            return True
            
        return False
    
    async def _solve_cloudflare_turnstile(self, page: Page, url: str) -> bool:
        """
        Solve Cloudflare Turnstile challenge using 2Captcha
        Returns True if solved successfully
        """
        try:
            html = await page.content()
            
            # Try to find Turnstile sitekey
            sitekey_match = re.search(r'data-sitekey="([^"]+)"', html)
            if not sitekey_match:
                # Try alternative patterns
                sitekey_match = re.search(r'sitekey["\']?\s*[:=]\s*["\']([^"\'\']+)', html)
            
            if not sitekey_match:
                print("  [!] Could not find Turnstile sitekey")
                print("  [~] Trying fallback: waiting for JS Challenge auto-solve...")
                # Wait for Cloudflare JS Challenge to auto-solve (10 seconds)
                await asyncio.sleep(10)
                return True  # Return True to indicate we tried
            
            sitekey = sitekey_match.group(1)
            print(f"  [~] Found sitekey: {sitekey[:20]}...")
            
            # Submit to 2Captcha
            print("  [~] Submitting to 2Captcha (this may take 10-60 seconds)...")
            result = self.captcha_solver.turnstile(
                sitekey=sitekey,
                url=url
            )
            
            token = result['code']
            print(f"  [✓] Got solution token: {token[:20]}...")
            
            # Inject token into page
            inject_script = f"""
            (function() {{
                // Find Turnstile response field
                let responseField = document.querySelector('[name="cf-turnstile-response"]');
                if (!responseField) {{
                    responseField = document.querySelector('input[name*="turnstile"]');
                }}
                
                if (responseField) {{
                    responseField.value = '{token}';
                    
                    // Trigger change event
                    responseField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    // Try to find and submit form
                    let form = responseField.closest('form');
                    if (form) {{
                        form.submit();
                    }}
                    
                    return true;
                }} else {{
                    // Try alternative: call Turnstile callback directly
                    if (window.turnstile && window.turnstile.reset) {{
                        window.turnstile.reset();
                    }}
                    return false;
                }}
            }})()
            """
            
            injection_result = await page.evaluate(inject_script)
            if injection_result:
                print("  [✓] Token injected successfully")
            else:
                print("  [!] Could not inject token (trying page reload)")
                await page.reload(wait_until='networkidle')
            
            return True
            
        except Exception as e:
            print(f"  [!] 2Captcha error: {str(e)[:100]}")
            return False
    
    async def close(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


async def main():
    """Demo: fetch one URL"""
    bypass = CloudflareBypass()
    
    try:
        # Test WITH proxy by default
        print("Testing WITH proxy...")
        await bypass.setup_browser(use_proxy=True)
        
        url = "https://www.iherb.com/pr/now-foods-omega-3-180-epa-120-dha-200-softgels/424"
        success, html = await bypass.fetch_page(url)
        
        if success:
            print(f"[OK] Success! Got {len(html)} bytes of HTML")
            print(f"First 200 chars: {html[:200]}")
        else:
            print(f"[X] Failed: {html}")
    
    finally:
        await bypass.close()


if __name__ == "__main__":
    asyncio.run(main())
