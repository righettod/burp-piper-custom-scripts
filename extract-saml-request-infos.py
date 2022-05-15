import sys
import base64
import re
import xml.etree.ElementTree as ET  # nosec B405
import zlib
import urllib.parse
"""
PIPER script to extract and pretty-display information from a SAML request present in an HTTP request.
Target tool: Message viewers
Require that HTTP headers been passed
No filters needed
"""

DEFAULT_ENCODING = "utf-8"


def decode(saml_content):
    # Taken from
    # https://github.com/onelogin/python-saml/blob/master/src/onelogin/saml2/utils.py#L98
    decoded = urllib.parse.unquote(saml_content)
    decoded = base64.b64decode(decoded.encode(DEFAULT_ENCODING))
    try:
        result = zlib.decompress(decoded, -15)
    except Exception:
        result = decoded
    return result.decode(DEFAULT_ENCODING)


def pretty_print(saml_content):
    element = ET.XML(saml_content)
    ET.indent(element)
    return ET.tostring(element, encoding='unicode')


# Match pattern representing a SAML request structure like the following:
# SAMLRequest=xxxx
expr = r'SAMLRequest=([a-zA-Z0-9%_\-=/+]+)'
# Extract the whole request content
request = "".join(sys.stdin)
# Extract any SAML request
saml_requests = re.findall(expr, request, re.MULTILINE)
count = len(saml_requests)
if count == 0:
    print("No SAML request found.")
else:
    print(f"{count} SAML request found.")
    for saml_request in saml_requests:
        try:
            saml_request_formatted = pretty_print(decode(saml_request))
            print("[+] XML formatted:")
            print(saml_request_formatted)
        except Exception as e:
            print(f"[!] Error during processing of SAML request '{saml_request}':\n{str(e)}")
