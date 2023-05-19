import random
import base64

def is_prime(n, k=5):
    """
    Miller-Rabin primality test.
    """
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime_number(n):
    """
    Generate a prime number with n bits.
    """
    while True:
        p = random.getrandbits(n)
        if is_prime(p):
            return p

def gcd(a, b):
    """
    Compute the greatest common divisor of a and b.
    """
    while b:
        a, b = b, a % b
    return a

def multiplicative_inverse(e, phi):
    """
    Compute the multiplicative inverse of e modulo phi.
    """
    def extended_gcd(a, b):
        if b == 0:
            return (a, 1, 0)
        else:
            d, x, y = extended_gcd(b, a % b)
            return (d, y, x - (a // b) * y)

    d, x, _ = extended_gcd(e, phi)
    if d == 1:
        return x % phi

def generate_key_pair(bit_length):
    """
    Generate a public-private key pair with the given bit length.
    """
    p = generate_prime_number(bit_length // 2)
    q = generate_prime_number(bit_length // 2)
    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)

    d = multiplicative_inverse(e, phi)

    public_key = (n, e)
    private_key = (n, d)

    return public_key, private_key

def encrypt(message: bytes, public_key: tuple) -> bytes:
    # Unpack the public key into its components
    n, e = public_key

    # Split the message into 1024-byte chunks
    chunks = [message[i:i+1024] for i in range(0, len(message), 1024)]

    # Encrypt each chunk using the public key
    encrypted_chunks = []
    for chunk in chunks:
        m = int.from_bytes(chunk, byteorder='big')
        c = pow(m, e, n)
        encrypted_chunk = c.to_bytes((c.bit_length() + 7) // 8, byteorder='big')
        encrypted_chunks.append(encrypted_chunk)

    # Concatenate the encrypted chunks and return the result
    return b''.join(encrypted_chunks)


def decrypt(encrypted: bytes, private_key: tuple) -> bytes:
    # Unpack the private key into its components
    n, d = private_key

    # Split the encrypted message into 1024-byte chunks
    encrypted_chunks = [encrypted[i:i+128] for i in range(0, len(encrypted), 128)]

    # Decrypt each chunk using the private key
    decrypted_chunks = []
    for encrypted_chunk in encrypted_chunks:
        c = int.from_bytes(encrypted_chunk, byteorder='big')
        m = pow(c, d, n)
        decrypted_chunk = m.to_bytes((m.bit_length() + 7) // 8, byteorder='big')
        decrypted_chunks.append(decrypted_chunk)

    # Concatenate the decrypted chunks and return the result
    return b''.join(decrypted_chunks)




