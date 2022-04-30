import sys
import base64
import urllib.parse
import re
import xml.etree.ElementTree as ET  # nosec B405
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
"""
PIPER script to extract and pretty-display information from a SAML response present in an HTTP response.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: [a-z]+\/x?(html)
"""

DEFAULT_ENCODING = "utf-8"
SAML_NAMESPACES = {"ds": "http://www.w3.org/2000/09/xmldsig#", "samlp": "urn:oasis:names:tc:SAML:2.0:protocol", "saml": "urn:oasis:names:tc:SAML:2.0:assertion"}


def extract_nodes(xpath_expr, saml_content):
    # See here for XXE exposure:
    # https://www.shiftleft.io/community-and-training/vulnerability-fix-database/xml-external-entity-attacks-python/
    # https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#python
    nodes = []
    if "<!DOCTYPE" in re.sub(r'([\s|\n|\t|\r]*)', "", saml_content.upper()):
        print("[!] DTD/External Entity detected so skip processing...")
    else:
        root = ET.fromstring(saml_content)  # nosec B314
        nodes = root.findall(xpath_expr, SAML_NAMESPACES)
    return nodes


def pretty_print(saml_content):
    element = ET.XML(saml_content)
    ET.indent(element)
    return ET.tostring(element, encoding='unicode')


def signature_omits_comments(saml_content):
    # See explanation on https://duo.com/blog/duo-finds-saml-vulnerabilities-affecting-multiple-implementations
    algos_not_omitting_comments_in_signature = ["http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments",
                                                "http://www.w3.org/2001/10/xml-exc-c14n#WithComments",
                                                "http://www.w3.org/2006/12/xml-c14n11#WithComments"]
    result = True
    nodes = extract_nodes(".//ds:CanonicalizationMethod", saml_content)
    for node in nodes:
        if node.attrib["Algorithm"] in algos_not_omitting_comments_in_signature:
            result = False
    return result


def extract_algorithms_used(saml_content):
    algos = {"Signature": [], "Digest": []}
    for type_algo in algos:
        nodes = extract_nodes(f".//ds:{type_algo}Method", saml_content)
        for node in nodes:
            alg = node.attrib["Algorithm"].split("#")[1].lower().strip()
            if alg not in algos[type_algo]:
                algos[type_algo].append(alg)
    return algos


def extract_certificate_infos(saml_content):
    certs = []
    nodes = extract_nodes(".//ds:X509Certificate", saml_content)
    for node in nodes:
        cert_base64 = node.text
        pem_data = base64.b64decode(cert_base64.encode(DEFAULT_ENCODING))
        certif = x509.load_der_x509_certificate(pem_data, default_backend())
        certs.append({"Fingerprint": certif.fingerprint(hashes.SHA256()).hex(),
                      "Version": certif.version,
                      "Issuer": certif.issuer,
                      "Subject": certif.subject,
                      "NotValidBefore": certif.not_valid_before,
                      "NotValidAfter": certif.not_valid_after})
    return certs


def extract_infos(saml_content):
    content = urllib.parse.unquote(saml_content)
    xml = base64.b64decode(content.encode(DEFAULT_ENCODING)).decode(DEFAULT_ENCODING)
    infos = {"signature_omits_comments": signature_omits_comments(xml),
             "algorithms_used": extract_algorithms_used(xml),
             "certificate_infos": extract_certificate_infos(xml),
             "xml": xml}
    return infos


# Match pattern representing a SAML response structure like the following:
# SAMLResponse=xxxx
expr = r'(?:name|id)=(?:"|\')SAMLResponse(?:"|\')\s+value=(?:"|\')([a-zA-Z0-9%_\-=/+]+)(?:"|\')'
# Extract the whole response content
response = "".join(sys.stdin)
# Extract any SAML response
saml_responses = re.findall(expr, response, re.MULTILINE)
count = len(saml_responses)
if count == 0:
    print("No SAML response found.")
else:
    print(f"{count} SAML response found.")
    for saml_response in saml_responses:
        try:
            infos = extract_infos(saml_response)
            for key, value in infos.items():
                if key != "xml":
                    print(f"[+] {key.replace('_',' ').capitalize()}:")
                    print(value)
            print("[+] XML formatted:")
            print(pretty_print(infos["xml"]))
        except Exception as e:
            print(f"[!] Error during processing of SAML response '{saml_response}':\n{str(e)}")
