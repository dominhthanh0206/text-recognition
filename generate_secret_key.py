#!/usr/bin/env python3
"""
Script to generate a random secret key for Flask applications
"""
import secrets
import string

def generate_secret_key(length=32):
    """Generate a random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    key = generate_secret_key()
    print(f"Generated SECRET_KEY: {key}")
    print(f"\nAdd this to your .env file:")
    print(f"SECRET_KEY={key}")
    print(f"\nOr set it as environment variable in Railway:")
    print(f"Railway Variables: SECRET_KEY = {key}") 