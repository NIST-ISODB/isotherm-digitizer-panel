import hashlib

def material_ID(input_name):

    #Apply the MD5SUM hash to the input string
    md5_hash = hashlib.md5(input_name.encode('utf-8'))
    #The material Hash is:
    #  1) Hexadecimal Digest of the Hash, all lowercase
    #  2) prepended with "NIST-MATDB-"
    MATDB_hash = "NIST-MATDB-"+md5_hash.hexdigest().lower()
    return MATDB_hash
