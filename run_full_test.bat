@echo off
echo ============================================
echo iHerb Cloudflare Bypass - FULL STABILITY TEST
echo ============================================
echo.
echo This will test:
echo - 5 URLs
echo - 30 requests per URL
echo - With and without proxy
echo - Total: 300 requests
echo.
echo This may take 30-60 minutes...
echo.
pause

python stability_test.py

echo.
echo ============================================
echo Full test completed!
echo Check test_results_*.json for details
echo ============================================
pause
