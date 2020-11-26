import sys, re
"""
PIPER script to detect request to an API using the first request line.
Target tool: Highlighters
"""
rc = 0
# Match first request line like: GET /api/aclTrafic HTTP/1.1
expr = r'^[A-Z]+\s\/(api|service|v|rest)[s]?[0-9]*\/'
for line in sys.stdin:
    if len(line.strip("\r").strip("\n").strip(" ")) == 0:
        continue
    # Read only the first line
    if re.search(expr, line, re.IGNORECASE) is not None:
		# Return code to match in the config of PIPER
        rc = 1
    break
exit(rc)
