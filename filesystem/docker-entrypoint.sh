#!/bin/sh

# Start listening on HTTP
printf "[+] Starting HTTP Services\n"
gunicorn -D -w 5 app:app -b 0.0.0.0:80 --worker-class aiohttp.worker.GunicornWebWorker 

# Check to see if we are starting HTTPS as well

if [[ -z "${USE_HTTPS}" ]]; then
    printf "[+] Not using HTTPS\n"
else
    printf "[+] Configure HTTPS\n"

    # Generate a Certificate
    # Take this from a state file?

    if [[ -z "${HTTPS_CERT}" ]]; then
        printf "  [-] Creating Certificate with default values\n"
        openssl req -nodes -new -x509 -days 365 -keyout ca.key -out ca-crt.pem -subj "/C=US/ST=IL/L=None/O=example.com/OU=domain/CN=example.com/emailAddress=me@example.com"
    else
        printf "  [-] Creating Certificates from user provided string\n"
        openssl req -nodes -new -x509 -days 365 -keyout ca.key -out ca-crt.pem -subj "${SUBJECT}"
    fi

    # Start listening on HTTPS
    printf "[+] Starting HTTPS Services\n"
    gunicorn -D -w 5 --certfile=/opt/honeypot/ca-crt.pem --keyfile=/opt/honeypot/ca.key app:app -b 0.0.0.0:443 --worker-class aiohttp.worker.GunicornWebWorker
fi
# Now run the CMD
exec "$@"