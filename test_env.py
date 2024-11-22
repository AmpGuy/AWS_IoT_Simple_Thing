import os

# Add this debug code at the start of your script
print("Checking environment variables:")
print(f"Endpoint: {os.getenv('AWS_IOT_ENDPOINT')}")
print(f"Cert Path: {os.getenv('AWS_IOT_CERT_PATH')}")
print(f"Key Path: {os.getenv('AWS_IOT_PRIVATE_KEY_PATH')}")
print(f"CA Path: {os.getenv('AWS_IOT_ROOT_CA_PATH')}")
