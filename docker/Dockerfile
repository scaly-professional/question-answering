# Ubuntu Linux as the base image
FROM ubuntu:18.04

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# Install spaCy
RUN pip3 install --upgrade pip
RUN pip3 install spacy==2.1.0
RUN python3 -m spacy download en_core_web_lg
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m spacy download en_core_web_md

#Install neuralcoref
RUN pip install neuralcoref
RUN python3 -c 'import neuralcoref'

# Install scipy
RUN pip3 install scipy

# Install numpy
RUN pip3 install numpy

# Install nltk
RUN pip3 install nltk

# Install pytorch
RUN pip3 install torch torchvision

RUN python3 -m nltk.downloader punkt

# Add the files into container, under QA folder, modify this based on your need
RUN mkdir /QA
ADD README.md /QA
ADD ask /QA
ADD answer /QA
ADD /questioning/q_generator.py /QA
ADD /encoder/infersent1.pkl /QA
ADD /encoder/infersent2.pkl /QA
ADD /fastText/crawl-300d-2M.vec /QA

# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
