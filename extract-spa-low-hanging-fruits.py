import sys
import re
"""
PIPER script to extract elements from a SPA (Single Page Applicatin) html files and main JS bundles that can be interesting from security point of view.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: [a-z]+\/(javascript|x\-javascript|html)
"""
# Sources:
# https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity
# https://courses.pragmaticwebsecurity.com/courses/introduction-to-oauth-2-0-and-openid-connect
# https://github.com/righettod/toolbox-pentest-web/blob/master/docs/README.md#leverage-map-files-to-recover-the-spa-original-code
#
# Extract the whole response body
content = "".join(sys.stdin)
# Search for remote JS script or remote CSS loading without using Subresource Integrity feature
tags_without_sri = []
pattern = r'<(?:script|link)\s.*?(?:src|href)=[\'"](?:http:|https:)?//.*[\'"].*?/?>'
tags = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
for tag in tags:
    tag_lower = tag.lower()
    if "integrity=" not in tag_lower and ("stylesheet" in tag_lower or "<script" in tag_lower):
        tags_without_sri.append(tag)
print(f"Tag without SRI ({len(tags_without_sri)}):")
if len(tags_without_sri) > 0:
    tags_without_sri.sort()
    print("\n".join(tags_without_sri))
else:
    print("No tag found.")
# Search for OAuth / OpenID Connect initialization flow keywords
pattern = r'(?:issuer|clientId|client_id|clientSecret|client_secret|code_verifier|code_challenge|showDebugInformation)\s?(?:\:|\=)\s?[\'"]?.*[\'"]?'
identifiers = re.findall(pattern, content, re.MULTILINE)
print(f"\nOAuth/OIDC initialization flow keywords ({len(identifiers)}):")
if len(identifiers) > 0:
    identifiers.sort()
    print("\n".join(identifiers))
else:
    print("No keyword found.")
# Search for JS bundle source mapping file
# Example: "//# sourceMappingURL=main.7017cdf9.chunk.js.map"
pattern = r'sourceMappingURL\s?=\s?([\w\d\.\-_]+)'
map_file = re.findall(pattern, content, re.MULTILINE)
print(f"\nJS bundle source mapping file ({len(map_file)}):")
if len(map_file) > 0:
    map_file.sort()
    print("\n".join(map_file))
else:
    print("No source mapping file found.")
