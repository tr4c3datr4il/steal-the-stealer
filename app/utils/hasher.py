from hashlib import sha256
from marshal import dumps


def hash_object(obj):
    return sha256(dumps(obj)).hexdigest()

def hash_string(s):
    return sha256(s.encode()).hexdigest()