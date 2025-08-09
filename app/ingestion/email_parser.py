import mailparser

def parse_eml(path_or_bytes):
    # mailparser supports parse_from_file and parse_from_bytes
    if isinstance(path_or_bytes, (bytes, bytearray)):
        mp = mailparser.parse_from_bytes(path_or_bytes)
    else:
        mp = mailparser.parse_from_file(path_or_bytes)
    return {
        'from': mp.from_,
        'to': mp.to,
        'subject': mp.subject,
        'date': mp.date,
        'body': mp.body
    }