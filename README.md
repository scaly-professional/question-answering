Do not copy and use this code

# cmu-nlp-qna
Question Generation and Question Answering Project as implemented by team Savannah

## Getting started

### Setting up

Navigate to your working directory and clone the project

    git clone git@github.com:bglar/cmu-nlp-qna.git

### Install dependencies

Dependencies for this project are stored in the requirements.txt file. 
Use the following command in your terminal to install them:

    pip install -r requirements.txt

In some cases when using pip3 in python3 you might have to use the following command instead:

    pip3 install -r requirements.txt


## Usage

### Question generation

The ask program must have the following command-line interface:

    cd working_dir/src
    ./ask article.txt nquestions

Where article.txt is a path to an arbitrary plain text file (the document) and nquestions is an 
integer (the number of questions to be generated).

### Question answering

Run the following command to answer questions a question:

    cd working_dir/src
    ./answer article.txt questions.txt

Where article.txt is a path to an arbitrary plain text file (the document) and questions.txt is a path 
to an arbitrary file of questions (one question per line with no extraneous material).


## Building the Docker Image

Install docker

cd into the project directory `cmu-nlp-qna`

Run the following docker command to build the docker image:

    docker build --tag <image_name> .

The build command might take long but might be sped up on a faster internet connection.
It copies the code from the `src` directory into the working dir `/QA`. For development we also copy the data files but that might be unnecessary.
