# iHerb Cloudflare Bypass

Playwright-based script to bypass Cloudflare protection on iherb.com.

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Quick Test (Single URL)
```bash
python iherb_bypass.py
```

### Full Stability Test (5 URLs × 30 requests)
```bash
python stability_test.py
```

## Configuration

Edit `config.json` to:
- Add/modify proxy servers
- Change test URLs
- Adjust stealth settings (delays, retries, timeout)

## Features

- **Stealth Techniques:**
  - CDP patches to hide `navigator.webdriver`
  - Canvas fingerprint randomization
  - WebGL vendor spoofing
  - Realistic browser fingerprint

- **Proxy Support:**
  - HTTP/HTTPS proxies
  - SOCKS5 proxies (change port to 50101 in config)
  - Automatic rotation

- **Cloudflare Detection:**
  - Automatic retry with exponential backoff
  - Validates actual page content vs challenge page

- **2Captcha Integration (Optional):**
  - Automatically solves Cloudflare Turnstile challenges
  - Achieves 95-99% bypass success rate
  - Add your API key to `config.json`: `"captcha_api_key": "YOUR_KEY"`
  - Get API key from: https://2captcha.com
  - Cost: ~$0.003 per solve (~$3 per 1000 captchas)

## Test Results

Results are saved to `test_results_YYYYMMDD_HHMMSS.json`
Failed responses are saved to `debug_responses/` folder
