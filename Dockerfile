FROM python:3.11.6-slim

# Install SO dependencies
RUN apt update
RUN apt-get -y install skopeo

# Add user and group
RUN groupadd -r app
RUN useradd -g app app

# Home directory
RUN mkdir /home/app
RUN chown -R app:app /home/app

# Work directory
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN chown -R app:app /usr/src/app

# User activities
USER app

# Python virtual environment
RUN pip install virtualenv
ENV PATH="/home/app/.local/bin:${PATH}"
RUN virtualenv venv
RUN ["/bin/bash", "-c", "source venv/bin/activate"]

# Instal Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./registry_sync"]
