import sys
import json
"""
PIPER script to extract the collection of assemblies from a HTTP response describing the assemblies used by a Blazor WebAssembly application.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: application/json
"""
# Extract the whole response body
content = "".join(sys.stdin)
# Verify if the JSON contains the reference elements
# See https://github.com/righettod/burp-piper-custom-scripts/issues/1
metadata = json.loads(content)
if "resources" in metadata and "assembly" in metadata["resources"] and len(metadata["resources"]["assembly"]) > 0:
    # Extract the list of assemblies
    assemblies = {}
    for assembly in metadata["resources"]["assembly"]:
        assemblies[assembly] = f"/_framework/_bin/{assembly}"
    print(f"{len(assemblies)} assemblies found.")
    print("\nUse the following script to download them, update the variable 'BaseUrl' with the target domain (like 'https://myapp.com'):\n")
    # Generate the download script for the current OS:
    # Windows => PowerShell / Other => Bash
    script = ""
    if sys.platform.startswith("win"):
        script = "$BaseUrl=\"[REPLACE_ME]\"\n"
        for assembly in assemblies:
            script += f"Invoke-WebRequest -Uri \"$BaseUrl{assemblies[assembly]}\" -OutFile \"{assembly}\"\n"
    else:
        script = "BaseUrl=\"[REPLACE_ME]\"\n"
        for assembly in assemblies:
            script += f"curl $BaseUrl{assemblies[assembly]} --output {assembly}\n"
    print(script)
else:
    print("No assembly found.")
