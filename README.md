# LYVE TestKit

In the file docker-compose.yaml set the Easyplan address and port and set the UWB Origin:
``` yaml
  benthos:
    image: ci4rail/redpanda-connect-kyt:v2.1.0-rc.1
    depends_on:
      - traccar
    command:
      - "-c"
      - "/config/benthos-chemnitz.yaml"
    restart: always
    environment:
      EASYPLAN_IP: <EasyplanIP>
      EASYPLAN_PORT: <EasyplanPort>
      ORIGIN_LAT: 50.85456167496589
      ORIGIN_LON: 12.936004101931074
      ORIGIN_AZI: 111.83618954170703
    ports:
      - 11001:11001/udp
      - 4195:4195
    volumes:
        - ./benthos-io4edge:/config:ro
        - ./benthos-io4edge/logs:/root/logs:rw
```
* If Easyplan Host is another machine use the IP adress of this machine.
* If Easyplan runs your machine and your machine is a Linux host set `EASYPLAN_IP` to `172.17.0.1`
* If Easyplan runs your machine and your machine is a Mac host set `EASYPLAN_IP` to `docker.for.mac.localhost`
* If Easyplan runs your machine and your machine is a Windows host set `EASYPLAN_IP` to `host.docker.internal`

Then start the Docker Compose either using Docker Desktop or by running: `$ docker compose up`.

# Initial setup

Start all containers with docker compose.

Install psql
```
sudo apt install postgresql-client
```
and create db

```
psql -d "postgres" -h localhost -U user

CREATE DATABASE raw_pos;
```

Then restart benthos
```
docker-compose restart benthos
```

In the folder tracelet_parameter you will find a collection of parameter for the tracelet. Use the io4edge-cli tool to apply a set of parameter:
```
io4edge-cli -i <tracelet-ip>:443 load-parameterset pos <parameter-json>
```

# Login into traccar


```
http://localhost:8082

# Register admin user on first login
Name: admin
EMail: admin@admin.de
Password: admin

# Then login with these credentials
```

# Register devices

In case device-id in tracelet is set to `TRACELET-1`:

## UWB Device
Name=TRACELET-1-UWB
Identifier=TRACELET-1-UWB

## GNSS Device
Name=TRACELET-1-GNSS
Identifier=TRACELET-1-GNSS

## FUSED Device
Name=TRACELET-1
Identifier=TRACELET-1

## Configure units
Settings->Server->Speed Unit=km/h

# View Grafana Dashboard

1. Open your web browser and navigate to [http://localhost:3000](http://localhost:3000).  
2. Log in with the following credentials:  
   - **Username:** `admin`  
   - **Password:** `ci4rail`  
3. Go to **Dashboards** and select the one you want to view.  

> **Note:** If this is the first time the Grafana container is started (or its volume has been deleted), click on **New** and import `dashboard-single-tracelet.json`.

# Log Files

Benthos starts an output task that writes every tracelet message into a json (Path: benthos-io4edge/logs).

## Convert Benthos Logs to Easyplan JSON

The log files can be converted to easyplan jsons with the script script/convert_benthos_to_easyplan.py.

### Usage

python3 convert_benthos_to_easyplan.py [-h] [-o OUTPUT] [--chunk-minutes CHUNK_MINUTES] [--from FROM_TS] [--to TO_TS] input

#### positional arguments:
* input: Path to Benthos log JSON file.

#### options:
* -h, --help: show help message and exit
* -o OUTPUT, --output OUTPUT: Output path for Easyplan JSON (defaults to stdout).
* --chunk-minutes CHUNK_MINUTES: Chunk length in minutes (<=0 disables chunking).
* --from FROM_TS: Start time (inclusive). ISO8601 (e.g. 2025-12-17T13:00:00Z or 2025-12-17T13:00:00+01:00); if no timezone is given, local time is assumed. Also accepts epoch ms.
* --to TO_TS: End time (inclusive). ISO8601 (e.g. 2025-12-17T14:00:00Z or 2025-12-17T14:00:00+01:00); if no timezone is given, local time is assumed. Also accepts epoch ms.


