# Ubuntu Linux as the base image
FROM ubuntu:18.04

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# Install spaCy (2.1.0 because of compatibility issues with neuralcoref)
RUN pip3 install --upgrade pip
RUN pip3 install spacy==2.1.0
RUN python3 -m spacy download en_core_web_md
RUN pip install neuralcoref
RUN python3 -c 'import neuralcoref'

RUN mkdir /QA
ADD src/ /QA/

# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
