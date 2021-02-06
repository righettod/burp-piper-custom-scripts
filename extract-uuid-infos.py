import sys
import uuid
import re
from datetime import datetime
"""
PIPER script to extract the collection of UUID present in a HTTP response and then, depending on the version of UUID, extract the infos for each of them.
Target tool: Message viewers
Require that HTTP headers NOT been passed
No filters needed
"""
# Sources:
# https://versprite.com/blog/universally-unique-identifiers/
# https://blog.silentsignal.eu/2017/02/17/not-so-unique-snowflakes/
# https://www.uuidtools.com/uuid-versions-explained
#
# Inspired from this project so credits goes first to it:
# https://github.com/silentsignal/burp-uuid
#
# Constants
NUM_100NS_INTERVALS_SINCE_UUID_EPOCH = 122192928000000000


# Utility function
def extract_uuid_infos(target_uuid):
    infos = None
    try:
        # Verify that the parameter passed in a valid UUID
        uuid_item = uuid.UUID(target_uuid)
        version = uuid_item.version
        infos = f"V{version} - '{target_uuid}' - "
        # Extract infos based on version
        if version == 1:
            epch = (uuid_item.time - NUM_100NS_INTERVALS_SINCE_UUID_EPOCH) / 10000
            dtime = datetime.fromtimestamp(epch / 1000)
            node_part = target_uuid.split("-")[4]
            mac = f"{node_part[0:2]}:{node_part[2:4]}:{node_part[4:6]}:{node_part[6:8]}:{node_part[8:10]}:{node_part[10:]}".upper()
            infos += f"Generation time '{dtime}' - Node MAC Address '{mac}' - ClockID/ClockSequence '{uuid_item.clock_seq}'."
        elif version == 2:
            infos += "Least significant 8 bits of the clock sequence are replaced by a 'local domain' number and least significant 32 bits of the timestamp are replaced by an integer identifier meaningful within the specified local domain."
        elif version == 3:
            infos += "MD5(NAMESPACE_IDENTIFIER + NAME)."
        elif version == 4:
            infos += "UUID could be duplicated (low chances) so manual check needed for entropy potential issues."
        elif version == 5:
            infos += "SHA1(NAMESPACE_IDENTIFIER + NAME)."
        else:
            infos += " Unknown version."
    except Exception:
        infos = None
    return infos


# Extract the whole response body
content = "".join(sys.stdin)
# Extract all UUID from the response body
expr = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
uuids = re.findall(expr, content, re.MULTILINE)
# Process the list
if len(uuids) == 0:
    print("No UUID found.")
else:
    infos_collection = []
    for uuid_item in uuids:
        infos = extract_uuid_infos(uuid_item)
        if infos is not None:
            infos_collection.append(infos)
    msg_count = len(infos_collection)
    if msg_count == 0:
        print("No UUID found.")
    else:
        print(f"{msg_count} UUID found.\n")
        infos_collection.sort()
        print("\n".join(infos_collection))
