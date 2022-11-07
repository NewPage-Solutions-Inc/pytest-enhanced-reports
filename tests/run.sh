echo '{"capabilities": {"browser": "Chrome","goog:loggingPrefs": {"browser": "ALL"}}}' > capabilities-js-test.json
pytest --driver Chrome \
  --driver-path deb/chromedriver \
  --alluredir=reports \
  --variables capabilities-js-test.json \
  --report_capture_browser_console_log 'always'
