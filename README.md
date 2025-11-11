# LYVE TestKit

In the file benthos-io4edge/benthos-chemnitz.yaml, search for "MyIP:Port" and replace it with your Easyplan address:
* If Easyplan Host is another machine use the IP adress of this machine.
* If Easyplan runs your machine and your machine is a Linux host replace "MyIP" with `172.17.0.1`
* If Easyplan runs your machine and your machine is a Mac host replace "MyIP" with `docker.for.mac.localhost`
* If Easyplan runs your machine and your machine is a Windows host replace "MyIP" with `host.docker.internal`

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

```

