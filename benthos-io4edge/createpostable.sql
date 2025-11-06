CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

CREATE TABLE IF NOT EXISTS pos_cmmc (
    devicetime timestamptz NOT NULL,
    servertime timestamptz NOT NULL,
    tracelet_id text NOT NULL,
    ignition boolean DEFAULT false,
    gnss_valid boolean DEFAULT false,
    gnss_latitude double precision,
    gnss_longitude double precision,
    gnss_altitude double precision,
    gnss_eph real DEFAULT 1000,
    gnss_epv real DEFAULT 1000,
    gnss_fixtype smallint DEFAULT 0,
    gnss_head_motion real,
    gnss_head_vehicle real,
    gnss_head_valid int8,
    gnss_speed real,
    uwb_valid boolean DEFAULT false,
    uwb_x double precision,
    uwb_y double precision,
    uwb_z double precision,
    uwb_siteid bigint,
    uwb_location_signature text,
    uwb_eph real DEFAULT 1000,
    uwb_fixtype smallint DEFAULT 0,
    uwb_head_motion real,
    uwb_head_vehicle real,
    uwb_head_valid smallint,
    uwb_speed real,
    speed real,
    mileage bigint
);

SELECT create_hypertable('pos_cmmc', by_range('devicetime'));