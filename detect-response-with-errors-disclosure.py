import sys
import re
"""
PIPER script to detect HTTP responses containing a strack trace.
Target tool: Highlighters
Require that HTTP headers NOT been passed
No filters needed
"""
rc = 0
# Match any regex defined with strack trace patterns
exprs = []
# Inspired by https://github.com/PortSwigger/error-message-checks/blob/master/src/main/resources/burp/match-rules.tab
# Java
# See https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/Throwable.html
exprs.append(r'(java\.[\w]+\.[\w]+)')
# .Net
# See https://docs.microsoft.com/en-us/dotnet/api/system.exception?view=net-5.0
exprs.append(r'(\[\w+Exception:\s[\w\d\s]+)')
# NodeJS
# Based on search on Google for examples and tunned to prevent false positives
exprs.append(r'(at\stryModuleLoad\s\()')
# Go
# See https://www.ardanlabs.com/blog/2015/01/stack-traces-in-go.html
# See https://www.bugsnag.com/blog/go-errors
exprs.append(r'(panic:)')
# Python
# See https://docs.python.org/3/tutorial/errors.html
exprs.append(r'(Traceback)')
# Ruby
# See https://blog.appsignal.com/2018/02/06/reading-and-understanding-ruby-stack-traces.html
exprs.append(r'(\.rb:\d+:in)')
# Kotlin - Handled by the Java regexes
# PHP
# Based on search on Google for examples
exprs.append(r'(\.php\son\sline\s\d+)')
# DB
# Based on search on Google for examples
exprs.append(r'(ODBC\sDriver\s\d+\sfor\sSQL\sServer)')
# Extract the whole response body
# Remove all comments (single line and multiline) to prevent false positive
single_line_comment_regex = r'^[\s\t]*\/\/.*$'
multi_line_comment_regex = r'^[\s\t]*\/\*.*?\*\/'
multi_line_comment_regex_additional_line = r'^[\s\t]*\*.*'
content = ""
for line in sys.stdin:
    if (re.search(single_line_comment_regex, line, re.IGNORECASE) is None and re.search(multi_line_comment_regex, line, re.IGNORECASE | re.MULTILINE) is None and re.search(multi_line_comment_regex_additional_line, line, re.IGNORECASE | re.MULTILINE) is None):
        content += line
# Search for the presence of patterns in the response body
for expr in exprs:
    if re.search(expr, content, re.IGNORECASE | re.MULTILINE) is not None:
        # print(expr)
        # Return code to match in the config of PIPER
        rc = 1
        # Exit on first found
        break
exit(rc)
