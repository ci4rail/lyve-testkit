# LYVE TestKit


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

# Provision Grafana Dashboard

```

