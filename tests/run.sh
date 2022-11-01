# tests are declared here

# run tests to output js logs
rm -rf reports reports2
echo '{"capabilities": {"browser": "Chrome","goog:loggingPrefs": {"browser": "ALL"}}}' > capabilities-js-test.json
pytest --driver Chrome \
  --alluredir=reports \
  --driver-path deb/chromedriver \
  --variables capabilities-js-test.json \
  --report_capture_browser_console_log='always' \
  -k 'run_test_js_logs'

rm -rf capabilities-js-test.json
mv reports/*.json reports/allure-output.json
# test for output js logs
pytest --driver Chrome \
  --alluredir=reports2 \
  --driver-path deb/chromedriver \
  -k 'test_js_logs_functionality'
rm -rf reports reports2


# test clean up data
#pytest --driver Chrome \
#  --alluredir=reports \
#  --driver-path deb/chromedriver \
#  --variables capabilities-js-test.json \
#  --report_capture_browser_console_log='always' \
#  -k 'test_js_logs'


