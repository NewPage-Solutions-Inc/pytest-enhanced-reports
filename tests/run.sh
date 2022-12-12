# python -m pytest --alluredir=reports --report_capture_browser_console_log 'always'
pytest -s -vv --disable-warnings --headless=False --report_browser_console_log_capture_frequency='always' --alluredir='reports'
