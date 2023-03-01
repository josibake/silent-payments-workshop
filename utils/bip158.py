from typing import List
import bitstring

def rotl64(n, b):
    return n >> (64 - b) | (n & ((1 << (64 - b)) - 1)) << b

def siphash_round(v0, v1, v2, v3):
    v0 = (v0 + v1) & ((1 << 64) - 1)
    v1 = rotl64(v1, 13)
    v1 ^= v0
    v0 = rotl64(v0, 32)
    v2 = (v2 + v3) & ((1 << 64) - 1)
    v3 = rotl64(v3, 16)
    v3 ^= v2
    v0 = (v0 + v3) & ((1 << 64) - 1)
    v3 = rotl64(v3, 21)
    v3 ^= v0
    v2 = (v2 + v1) & ((1 << 64) - 1)
    v1 = rotl64(v1, 17)
    v1 ^= v2
    v2 = rotl64(v2, 32)
    return (v0, v1, v2, v3)

def siphash(k0, k1, data):
    assert type(data) == bytes
    v0 = 0x736f6d6570736575 ^ k0
    v1 = 0x646f72616e646f6d ^ k1
    v2 = 0x6c7967656e657261 ^ k0
    v3 = 0x7465646279746573 ^ k1
    c = 0
    t = 0
    for d in data:
        t |= d << (8 * (c % 8))
        c = (c + 1) & 0xff
        if (c & 7) == 0:
            v3 ^= t
            v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
            v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
            v0 ^= t
            t = 0
    t = t | (c << 56)
    v3 ^= t
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    v0 ^= t
    v2 ^= 0xff
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    v0, v1, v2, v3 = siphash_round(v0, v1, v2, v3)
    return v0 ^ v1 ^ v2 ^ v3

def bip158_basic_element_hash(script_pub_key, N, block_hash):
    """ Calculates the ranged hash of a filter element as defined in BIP158:

    'The first step in the filter construction is hashing the variable-sized
    raw items in the set to the range [0, F), where F = N * M.'

    'The items are first passed through the pseudorandom function SipHash, which takes a
    128-bit key k and a variable-sized byte vector and produces a uniformly random 64-bit
    output. Implementations of this BIP MUST use the SipHash parameters c = 2 and d = 4.'

    'The parameter k MUST be set to the first 16 bytes of the hash (in standard
    little-endian representation) of the block for which the filter is constructed. This
    ensures the key is deterministic while still varying from block to block.'
    """
    M = 784931
    block_hash_bytes = bytes.fromhex(block_hash)[::-1]
    k0 = int.from_bytes(block_hash_bytes[0:8], 'little')
    k1 = int.from_bytes(block_hash_bytes[8:16], 'little')
    return (siphash(k0, k1, script_pub_key) * (N * M)) >> 64

def gcs_match_any(key: hex, targets: List[hex], gcs_data: dict) -> bool:

    compressed_set = gcs_data['filter']
    N = gcs_data['size']
    P = 19

    target_hashes = []
    for target in targets:
        target_bytes = bytes.fromhex(target)
        target_hash = bip158_basic_element_hash(target_bytes, N, key)
        target_hashes.append(target_hash)

    # Sort targets so matching can be checked in linear time.
    target_hashes.sort()

    stream = bitstring.BitStream(hex=compressed_set)

    value = 0
    target_idx = 0
    target_val = target_hashes[target_idx]

    for _ in range(N):
        delta = golomb_decode(stream, P)
        value += delta

        while True:
            if target_val == value:
                return True

            # Move on to the next set value.
            elif target_val > value:
                break

            # Move on to the next target value.
            else:
                target_idx += 1

                # If there are no targets left, then there are no matches.
                if target_idx == len(targets):
                    return False

                target_val = target_hashes[target_idx]

    return False

def golomb_decode(stream, P):
    q = 0
    while stream.read(1):
        q += 1

    r = int(stream.read(P).bin, 2)
    x = (q << P) + r
    return x
