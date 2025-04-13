import re

input_file = "../gem5/m5out/debug.log"
output_file = "/home/brianmcmanus/illinois/booksim/booksim_trace.txt"

# Match lines like:
# 123456789012345: PerfectSwitch-0: Message: [ResponseMsg: addr = [0xdeadbeef, line 0xdeadbeef] Type = DATA_EXCLUSIVE Sender = L2Cache-1 Destination = [NetDest ...]
pattern = re.compile(
    r"^(\d+): .*?Message: \[ResponseMsg: addr = \[0x([0-9A-Fa-f]+), line 0x[0-9A-Fa-f]+\]\s*"
    r"Type = (\w+)\s+Sender = ([\w-]+)\s+Destination = .*?([\w-]+)\s*\]"
)

# Packet size defaults
packet_size_map = {
    "MEMORY_DATA": 16,
    "DATA_EXCLUSIVE": 16,
    "EXCLUSIVE_UNBLOCK": 4,
    "UNKNOWN": 4,
}

# Track type IDs
msg_type_to_id = {}
type_id_to_size = []
next_type_id = 0

# Node ID map
node_map = {}
next_node_id = 0

def get_node_id(name):
    global next_node_id
    if name not in node_map:
        node_map[name] = next_node_id
        next_node_id += 1
    return node_map[name]

# First pass to get the initial timestamp
timestamps = []

with open(input_file, "r") as infile:
    for line in infile:
        match = pattern.search(line)
        if match:
            timestamps.append(int(match.group(1)))

if not timestamps:
    raise ValueError("No matching messages found in the log!")

first_timestamp = min(timestamps)

# Second pass to write normalized trace
with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        match = pattern.search(line)
        if match:
            raw_time = int(match.group(1))
            delay = (raw_time - first_timestamp)//1000

            msg_type = match.group(3)
            sender = match.group(4)
            receiver = match.group(5)

            src = get_node_id(sender)
            dst = get_node_id(receiver)

            size = packet_size_map.get(msg_type, packet_size_map["UNKNOWN"])

            # Assign a type ID for BookSim (optional)
            if msg_type not in msg_type_to_id:
                msg_type_to_id[msg_type] = next_type_id
                type_id_to_size.append(size)
                next_type_id += 1

            type_id = msg_type_to_id[msg_type]

            outfile.write(f"{delay} {src} {dst} {type_id}\n")

# Optional: Print mappings for reference
print("=== Node ID Mapping ===")
for name, nid in node_map.items():
    print(f"{nid}: {name}")

print("\n=== Message Type Mapping ===")
for name, tid in msg_type_to_id.items():
    print(f"{tid}: {name}, size={packet_size_map.get(name, 4)}")
