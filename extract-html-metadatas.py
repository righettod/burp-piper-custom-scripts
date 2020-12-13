import sys, re
"""
PIPER script to extract interesting information from HTML META tags from a HTTP response.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: [a-z]+\/x?(html)
"""
# Match all meta tags pattern holding "generator" and "framework" information 
# whatever the order of the attributes NAME and CONTENT
exprs = []
exprs.append(r'<meta\sname=[\'"](framework|generator)[\'"]\scontent=[\'"]([\d\w\.\s\-,\/:\(\)]+)[\'"]\s*\/?>')
exprs.append(r'<meta\scontent=[\'"]([\d\w\.\s\-,\/:\(\)]+)[\'"]\sname=[\'"](framework|generator)[\'"]\s*\/?>')
# Extract the whole response body
content = "".join(sys.stdin)
# Extract the metadatas via the regex and handle duplicates
results = []
## First regex working on order 1) NAME 2) CONTENT
metadatas = re.findall(exprs[0], content, re.IGNORECASE|re.MULTILINE)
for metadata in metadatas:
    msg = f"{metadata[0].capitalize()}: {metadata[1]}"
    if msg not in results:
        results.append(msg)
## Second regex working on order 1) CONTENT 2) NAME
metadatas = re.findall(exprs[1], content, re.IGNORECASE|re.MULTILINE)
for metadata in metadatas:
    msg = f"{metadata[1].capitalize()}: {metadata[0]}"
    if msg not in results:
        results.append(msg)
count = len(results)    
if count > 0:
    results.sort()
    print(f"{count} metadata(s) found:")
    print("\n".join(results))
else:
    print("No metadata found.")