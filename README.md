This example python code for establishing a connection to AWS IoT Core services authenticates with AWS and 
periodically transmits sensor data. It reads a discrete I/O pin and sends this state to AWS.
It sends pseudo temperature data in floating point to AWS as well.
It incorporates extensive fault handling.
To run the code, one would have to create a thing, provide credentials under their own AWS account and edit the startup.sh file with these 
filenames and endpoint string.
Then simply run on the thing ./startup.sh from the CLI.
