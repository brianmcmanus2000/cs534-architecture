import re

input_file = "../gem5/m5out/debug.log"
output_file = "DNNMark_trace.txt"

CONTROL_SIZE = 8
DATA_SIZE = 64

msg_start_pattern = re.compile(r'^\s*(\d+): .*?Message:\s*\[(\w+Msg):\s*addr\s*=')
type_pattern = re.compile(r'Type\s*=\s*(\w+)')
sender_pattern = re.compile(r'Sender\s*=\s*([\w-]+)')
netdest_pattern = re.compile(r'Destination\s*=\s*\[NetDest\s*\(\d+\)\s+([^\]]+)\]')
msgsize_pattern = re.compile(r'MessageSize\s*=\s*(\w+)')
requestor_pattern = re.compile(r'Requestor\s*=\s*([\w-]+)')

# sender_to_netdest = {
#     "Directory-0": 4,
#     "CorePair-0": 12,
#     "CorePair-1": 13,
#     "TCP-0": 15,
#     "TCP-1": 16,
#     "TCP-2": 17,
#     "TCP-3": 18,
#     "DMA-0": 20,
#     "TCC-0": 23,
#     "DMA-1": 24,  
#     "SQC-0": None,
#     "SQC-1": None,
#     "L3Cache-0": None,
#     "NULL-0": None
# } 

booksim_src_mapping={
        "Directory-0": 1,
        "CorePair-0": 2,
        "CorePair-1": 3,
        "TCP-0": 4,
        "TCP-1": 5,
        "TCP-2": 6,
        "TCP-3": 7,
        "TCC-0": 8,
        "SQC-0": 9,
        "SQC-1": 10,
        "L3Cache-0": 11,
        "NULL-0": 12
}
booksim_dst_mapping={
    4:1,
    12:2,
    13:3,
    15:4,
    16:5,
    17:6,
    18:7,
    20:9,
    23:8,
    24:10
}


with open(input_file, "r") as infile:
    for line in infile:
        time_match = msg_start_pattern.search(line)
        if time_match:
            first_timestamp = int(time_match.group(1))
            print(f"First timestamp: {first_timestamp}")
            break
    else:
        raise ValueError("No matching messages found in the log!")



with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        match = msg_start_pattern.search(line)
        if match:
            msg_time = int(match.group(1)) #get the tick the message was sent
            sender_match = sender_pattern.search(line)

            if sender_match:
                sender = sender_match.group(1)
            else: #sometimes there is no sender field but there is a requestor field, so we use that if possible
                requestor_match = requestor_pattern.search(line)
                if requestor_match:
                    sender = requestor_match.group(1)
                else:
                    sender = "UNKNOWN"

            netdest_match = netdest_pattern.search(line)
            netdest_raw = netdest_match.group(1).strip().split() #get the destination bits, as a list

            msgsize_match = msgsize_pattern.search(line)
            msg_size = msgsize_match.group(1).lower() if msgsize_match else "" #get the message size

            delay = (msg_time - first_timestamp) // 1000

            src = booksim_src_mapping[sender]
            size = DATA_SIZE if "data" in msg_size.lower() else CONTROL_SIZE
            type_id = 1 if size == DATA_SIZE else 0
            if(src!=None):
                for i, val in enumerate(netdest_raw):
                    if val == '1':
                        dst = booksim_dst_mapping[i]
                        outfile.write(f"{delay} {src} {dst} {type_id}\n")
                        # print(f"delay: {delay}, src: {src}, dst: {dst}, msg_size: {msg_size}, type_id: {type_id}")
print("=== Node ID Mapping ===")
print(booksim_src_mapping)

print("\n=== Message Type Mapping ===")
print("0: Control, size=8")
print("1: Data, size=64")
