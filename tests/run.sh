# clean up all videos + screenshots
rm -rf reports && mkdir -p reports
pytest -s -vv --disable-warnings \
  --headless=False \
  --report_browser_console_log_capture='always' \
  --alluredir='reports' \
  --report_keep_screenshots='False' \
  --report_keep_videos='False'

# keep videos + screenshots
rm -rf reports && mkdir -p reports
pytest -s -vv --disable-warnings \
  --headless=False \
  --report_browser_console_log_capture='always' \
  --alluredir='reports' \
  --report_keep_videos='True'
