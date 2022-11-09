echo '{"capabilities": {"headless": true, "browser": "Chrome","goog:loggingPrefs": {"browser": "ALL"}}}' > capabilities-js-test.json
python3.9 -m pytest --driver Chrome \
  --driver-path $CHROMEWEBDRIVER \
  --alluredir=reports \
  --headless=true \
  --variables capabilities-js-test.json \
  --report_capture_browser_console_log 'always'

