set -e
export AWS_IOT_ENDPOINT="a1yx8l5qf4gcx2-ats.iot.us-east-1.amazonaws.com"
export AWS_IOT_CERT_PATH="/home/thomas/raspberry_iot_app/certs/raspy_sensor_02.pem.crt"
export AWS_IOT_PRIVATE_KEY_PATH="/home/thomas/raspberry_iot_app/certs/raspy_sensor_02.private.key"
export AWS_IOT_PUBLIC_KEY_PATH="/home/thomas/raspberry_iot_app/certs/raspy_sensor_02.public.key"
export AWS_IOT_ROOT_CA_PATH="/home/thomas/raspberry_iot_app/certs/root-CA.pem"
export AWS_IOT_CLIENT_ID="raspy_sensor_02"

# Check for python 3
if ! python3 --version &> /dev/null; then
  printf "\nERROR: python3 must be installed.\n"
  exit 1
fi

# Check to see if root CA file exists, download if not
# if [ ! -f ./root-CA.crt ]; then
#   printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
#   curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
# fi

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python-v2 ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python-v2.git --recursive
fi

# Check to see if AWS Device SDK for Python is already installed, install if not
if ! python3 -c "import awsiot" &> /dev/null; then
  printf "\nInstalling AWS SDK...\n"
  python3 -m pip install ./aws-iot-device-sdk-python-v2
  result=$?
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install SDK.\n"
    exit $result
  fi
fi

# run pub/sub sample app using certificates downloaded in package
printf "\nRunning pub/sub sample application...\n"
python3 ./main_app1.py
