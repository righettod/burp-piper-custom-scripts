import sys
import re
"""
PIPER script to extract all occurences of unsafe patterns used in a SPA (Single Page Application) main JS bundle file.
Target tool: Message viewers
Require that HTTP headers NOT been passed
Filters needed via matching of the case insensitive regex for the header Content-Type: [a-z]+\/(javascript|x\-javascript)
"""
# Sources:
# https://pragmaticwebsecurity.com/articles/spasecurity/angular-xss.html
# https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part2.html
# https://pragmaticwebsecurity.com/articles/spasecurity/react-xss-part3.html
#
# Dictionary of patterns by framework:
#   KEY is the framework name in uppercase
#   VALUE is a array of regular expressions matching unsage patterns to extract
patterns = {}
patterns["ANGULAR"] = [r'bypassSecurity[A-Za-z0-9]+', r'[A-Za-z0-9]+\.renderer2\.[A-Za-z0-9]+']
patterns["REACT"] = [r'dangerouslySetInnerHTML\s?=\s?[\{\}_\-\.\"\'\s:\w\d]+', r'[A-Za-z0-9]+\.findDOMNode\(', r'React\.createRef\(']
# Extract the whole response body
content = "".join(sys.stdin)
# Apply extraction
total = 0
for framework in patterns:
    print(f"Search patterns for {framework}:")
    count = 0
    for pattern in patterns[framework]:
        data = re.findall(pattern, content, re.MULTILINE)
        if len(data) > 0:
            # Remove duplicate and sort the results
            result = []
            [result.append(f"  {item}") for item in data if f"  {item}" not in result]
            count += len(result)
            result.sort()
            print("\n".join(result))
    if count == 0:
        print("  No pattern found.")
    total += count
print("Summary:")
print(f"{total} patterns found.")
