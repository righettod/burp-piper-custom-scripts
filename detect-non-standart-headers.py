import sys
"""
PIPER script to detect if a HTTP response contains non standarts headers.
Target tool: Commentators
Require that HTTP headers been passed
No filters needed
"""
standard_response_headers = [
"accept-patch",
"accept-ranges",
"access-control-allow-credentials",
"access-control-allow-headers",
"access-control-allow-methods",
"access-control-allow-origin",
"access-control-expose-headers",
"access-control-max-age",
"age",
"allow",
"alt-svc",
"cache-control",
"connection",
"content-disposition",
"content-encoding",
"content-language",
"content-length",
"content-location",
"content-range",
"content-security-policy",
"content-transfer-encoding",
"content-type",
"cross-origin-resource-policy",
"date",
"delta-base",
"etag",
"expect-ct",
"expires",
"feature-policy",
"host",
"im",
"last-modified",
"link",
"location",
"pragma",
"proxy-authenticate",
"public-key-pins",
"referrer-policy",
"retry-after",
"server",
"set-cookie",
"strict-transport-security",
"tk",
"trailer",
"transfer-encoding",
"upgrade",
"vary",
"via",
"warning",
"www-authenticate",
"x-content-type-options",
"x-frame-options",
"x-permitted-cross-domain-policies",
"x-xss-protection"
]
lines = sys.stdin.readlines()
headers_find = []
for line in lines:
    # Skip first line
    if "HTTP/1.0" in line or "HTTP/1.1" in line or "HTTP/2" in line:
        continue
    if len(line.strip("\n").strip("\r").strip(" ")) == 0:
        # We reach the HTTP body so we exit
        break
    # Analyse line
    header_name = line.split(":")[0].strip(" ").lower()
    if header_name not in standard_response_headers:
        headers_find.append(header_name)
if len(headers_find) > 0:
    print(f"{len(headers_find)} non standard response headers found: {headers_find}")
