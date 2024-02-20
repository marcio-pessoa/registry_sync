# Registry Sync

Sync container images between two registries.

## Python virtual environment

```sh
# Creating virtual environment
python -m venv venv
```

```sh
# Activating virtual environment
source venv/bin/activate
```

```sh
# Leaving virtual environment
deactivate
```

## Dependencies

To run, please execute the following from the root directory:

```sh
venv/bin/pip install -r requirements.txt
```

## Usage

Direct usage:

```sh
registry_sync source_registry destination_registry:5000 -v INFO
```

Docker usage:

```sh
docker run registry_sync source_registry destination_registry
```
