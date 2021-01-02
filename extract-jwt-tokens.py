import sys, re, urllib.parse, base64, json, binascii
"""
PIPER script to extract and pretty-display all JWT tokens present in a HTTP response.
Target tool: Message viewers
Require that HTTP headers been passed
No filters needed
"""

# Utility function handling Base64 incorrect padding issue
def decode(encoded_data):
    has_error = True
    decoded_data = None
    work_data = encoded_data
    while has_error:
        try:
            decoded_data = base64.urlsafe_b64decode(work_data)
            has_error = False
            decoded_data = decoded_data.decode("ascii")
        except binascii.Error as e:
            if "incorrect padding" in str(e).lower():
                has_error = True
                work_data += "="
            else:
                has_error = False
                decoded_data = None
    return decoded_data

# Utility function handling the pretty print of the data
def pretty_print(jwt_data):
    content = "Data cannot be printed due to decoding issue."
    if jwt_data is not None:
        content = json.dumps(json.loads(jwt_data), indent=2, sort_keys=True)
    return content 

# Match pattern representing a JWT token structure like the following:
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ==
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ%3d%3d
expr = r'(eyJ[\w\.\-=%]+)'
# Extract the whole response content
response = "".join(sys.stdin)
# Extract all tokens
tokens_identified = re.findall(expr, response, re.MULTILINE)
# Verify that the tokens identified are valid JWT tokens
tokens = []
for token in tokens_identified:
    # JWT tokens are composed of 3 sections
    if len(token.split(".")) == 3:
        tokens.append(token)
count = len(tokens)
if count == 0:
    print("No token found.")
else:
    print(f"{count} token(s) found.")
    for token in tokens:
        try:
            token_url_decoded = urllib.parse.unquote(token)
            token_parts = token_url_decoded.split(".")
            token_header = decode(token_parts[0])
            token_payload = decode(token_parts[1])
            print(f"\n[+] Raw:\n{token_url_decoded}")
            print("[+] Header:")
            print(pretty_print(token_header))
            print("[+] Payload:")
            print(pretty_print(token_payload))
        except Exception as e:
            print(f"[!] Error during processing of token '{token}':\n{str(e)}")
