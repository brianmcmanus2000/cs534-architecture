import re

input_file = "m5out/debug.log"  # or whatever path you're using

# Match lines like:
# Message: [ResponseMsg: addr = ...
# Message: [UnblockMsg: addr = ...
msg_start_pattern = re.compile(r'^(\d+): .*?Message: \[(\w+Msg): addr =')
sender_pattern = re.compile(r'Sender\s*=\s*([\w-]+)')
requestor_pattern = re.compile(r'Requestor\s*=\s*([\w-]+)')
netdest_pattern = re.compile(r'Destination\s*=\s*\[NetDest\s*\(\d+\)\s+([^\]]+)\]')

seen_types = set()
counter = [0]*32
with open(input_file, "r") as infile:
    for line in infile:
        match = msg_start_pattern.search(line)
        if match:
            netdest_match = netdest_pattern.search(line)
            netdest_raw = netdest_match.group(1).strip().split()
            # sender_match = sender_pattern.search(line)
            # if sender_match:
            #     sender = sender_match.group(1)
            # else: #sometimes there is no sender field but there is a requestor field, so we use that if possible
            #     requestor_match = requestor_pattern.search(line)
            #     if requestor_match:
            #         sender = requestor_match.group(1)
            #     else:
            #         sender = "UNKNOWN"
            for i, val in enumerate(netdest_raw):
                # print(netdest_raw)
                # print(i)
                # print(val)
                if val == '1':
                    counter[i]+=1
print(counter)

# with open(input_file, "r") as infile:
#     for line in infile:
#         match = msg_start_pattern.search(line)
#         if match:
#             netdest_match = netdest_pattern.search(line)
#             netdest_raw = netdest_match.group(1)
#             if netdest_raw not in seen_types:
#                 seen_types.add(netdest_raw)
#                 print(line.strip())