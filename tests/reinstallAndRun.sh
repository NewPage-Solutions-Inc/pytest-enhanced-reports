
# Useful when debugging / testing during development

pip uninstall -y enhanced-reports

pip install ../src

# if the first parameter is 'y', delete logs file
if [ "$1" = "y" ]
then
  rm -f ./reports/tests.log
fi

pytest -vv --disable-warnings --headless=False --report_browser_console_log_capture_frequency='always' --alluredir='reports'
