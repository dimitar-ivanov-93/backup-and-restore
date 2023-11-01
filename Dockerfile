FROM arm64v8/postgres:latest
RUN apt-get update && apt-get install -y wget unzip gnupg gnupg2 curl apt-transport-https lsb-release ca-certificates
RUN mkdir -p /etc/apt/keyrings
RUN curl -sLS https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/keyrings/microsoft.gpg > /dev/null
RUN chmod go+r /etc/apt/keyrings/microsoft.gpg
RUN echo "deb [arch=`dpkg --print-architecture` signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/azure-cli.list
RUN apt-get update
RUN apt-get install -y azure-cli
# Copy the scripts into the Docker image
ADD scripts /scripts

# Make the scripts executable
RUN chmod +x /scripts/*
