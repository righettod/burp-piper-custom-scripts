import sys, re
"""
PIPER script to extract all API endpoints from a JS script content obtained from a HTTP response.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: [a-z]+\/(javascript|x\-javascript)
"""
# Match all URL patterns starting with ' or " and optionally followed by a /
# like '/api/v1/slo-ts/bo2o_ked/a6aa_bbb'
# like 'api/v1/slo-ts/bo2o_ked/a6aa_bbb'
expr = r'[\'"]\/?[\d\w_\-]+\/[\d\w_\-\/]+[\'"]'
# Extract the whole response body
script = "".join(sys.stdin)
# Extract the API endpoints via the regex and remove duplicates
endpoints = re.findall(expr, script, re.IGNORECASE|re.MULTILINE)
result = list(dict.fromkeys(endpoints))
count = len(result)
if count > 0:
    result.sort()
    print(f"{count} endpoint(s) found:")
    print("\n".join(result))
else:
    print("No endpoint found.")