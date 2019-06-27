# Get python slim or alpine. Alpine will be much smaller
FROM python:alpine

# Adding bash for Alpine doesn't carry it.
#RUN apk update
#RUN apk upgrade
RUN apk add --no-cache bash bash-completion
RUN apk add --no-cache openssh
#RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev make


# Copy and install requirements seperately for layered caching
#COPY /Users/adhawale/.ssh/kentik_id_rsa ~/.ssh/id_rsa

COPY ./requirements.txt /kkonsole/config/
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r /kkonsole/config/requirements.txt
#RUN pip install -r /kkonsole/config/requirements.txt
#RUN pip install paramiko
#RUN pip install ssh2-python

# Change workdir to the application
WORKDIR /kkonsole

# Copy everything else but requirements
COPY . /kkonsole

# The below RUN pip install . commands invoke the setup.py under kkonsole required for click
# Test run with --editable flag on
# --editable will allow you to update code and copy it to docker container and run the updated code without building the container again.
RUN pip install --editable .
#RUN pip install .

# Below -- commands for autocompletion in bash. <autocomplete href="http://click.palletsprojects.com/en/7.x/bashcomplete/"></autocomplete>
# THE BELOW RAN WHEN USED WITH --editable PIP PYTHON INSTALL AND MANUALLY ADDING THE BELOW COMMANDS. 
# TRY WITH PATH AS ROOT KKONSOLE DIR; AND/OR USING A .SH SCRIPT AND USING RUN IN DOCKERFILE
#CMD _KPERFORM_COMPLETE=source kperform > /kkonsole/config/kperform-complete.sh \
#    && touch ~/.bashrc \ 
#    && echo ". /kkonsole/config/kperform-complete.sh" > ~/.bashrc \
#    && source ~/.bashrc

#CMD ["python", "kkonsole.py"]
CMD ["/bin/bash"]
