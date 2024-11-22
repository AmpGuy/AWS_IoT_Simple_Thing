import boto3
import os

# Get the IoT client with explicit region
iot = boto3.client('iot', region_name='us-east-1')  # Replace with your region

# Get your account-specific endpoint
try:
    response = iot.describe_endpoint(
        endpointType='iot:Data-ATS'  # ATS endpoint
    )
    things = iot.list_things()
    print(f"Things list: {things}")
    print(f"Your ATS endpoint is: {response['endpointAddress']}")
    
    # You can also get the legacy VeriSign endpoint for comparison
    legacy_response = iot.describe_endpoint(
        endpointType='iot:Data'
    )

    print(f"Your endpoint is: {response['endpointAddress']}")
    print(f"Your configured endpoint is: {legacy_response['endpointAddress']}")

    # Verify they match
    if response['endpointAddress'] != legacy_response['endpointAddress']:
        print("WARNING: Endpoints don't match!")
    
except Exception as e:
    print(f"Error getting endpoint: {str(e)}")



