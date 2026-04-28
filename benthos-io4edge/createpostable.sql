CREATE TABLE IF NOT EXISTS rawpos (
  devicetime TIMESTAMPTZ,
  servertime TIMESTAMPTZ,

  tracelet_id TEXT,
  ignition BOOLEAN DEFAULT FALSE,

  firmware_version TEXT,
  uuid_str TEXT,
  ip_str TEXT,

  gnss_valid BOOLEAN DEFAULT FALSE,
  gnss_latitude DOUBLE PRECISION,
  gnss_longitude DOUBLE PRECISION,
  gnss_altitude DOUBLE PRECISION,
  gnss_eph DOUBLE PRECISION,
  gnss_epv DOUBLE PRECISION,
  gnss_fixtype INTEGER,
  gnss_head_motion DOUBLE PRECISION,
  gnss_head_vehicle DOUBLE PRECISION,
  gnss_head_valid BIGINT,
  gnss_head_precision REAL,
  gnss_speed DOUBLE PRECISION,

  uwb_valid BOOLEAN DEFAULT FALSE,
  uwb_x DOUBLE PRECISION,
  uwb_y DOUBLE PRECISION,
  uwb_z DOUBLE PRECISION,
  uwb_siteid BIGINT,
  uwb_location_signature TEXT,
  uwb_eph DOUBLE PRECISION,
  uwb_fixtype INTEGER,
  uwb_head_motion DOUBLE PRECISION,
  uwb_head_vehicle DOUBLE PRECISION,
  uwb_head_valid BIGINT,
  uwb_head_precision REAL,
  uwb_speed DOUBLE PRECISION,

  fused_valid BOOLEAN DEFAULT FALSE,
  fused_latitude DOUBLE PRECISION,
  fused_longitude DOUBLE PRECISION,
  fused_altitude DOUBLE PRECISION,
  fused_eph DOUBLE PRECISION,
  fused_head_motion DOUBLE PRECISION,
  fused_head_vehicle DOUBLE PRECISION,
  fused_head_valid BIGINT,
  fused_head_precision REAL,
  fused_speed DOUBLE PRECISION,

  direction INTEGER,
  speed DOUBLE PRECISION,
  mileage INTEGER,
  temperature DOUBLE PRECISION,

  metrics_valid BOOLEAN DEFAULT FALSE,

  metric__health_uwb_comm BIGINT,
  metric__health_uwb_firmware BIGINT,
  metric__health_uwb_config BIGINT,
  metric__health_gnss_comm BIGINT,
  metric__health_ubx_firmware BIGINT,
  metric__health_ubx_config BIGINT,
  metric__health_actors_startup BIGINT,

  metric__sntp_updates BIGINT,
  metric__free_heap_bytes BIGINT,
  metric__system_time_seconds DOUBLE PRECISION,
  metric__wifi_rssi_dbm DOUBLE PRECISION,
  metric__wifi_ap BIGINT,

  metric__gnss_num_sats_gps BIGINT,
  metric__gnss_num_sats_glonass BIGINT,
  metric__gnss_num_sats_beidou BIGINT,
  metric__gnss_num_sats_galileo BIGINT,
  metric__gnss_num_sats_qzss BIGINT,

  metric__gnss_uart_errors_hw_fifo BIGINT,
  metric__gnss_uart_errors_buf_full BIGINT,
  metric__gnss_uart_errors_char BIGINT,

  metric__gnss_num_sv BIGINT,
  metric__gnss_pga1 BIGINT,
  metric__gnss_pga2 BIGINT,
  metric__ubx_sensor_fusion_status BIGINT,
  metric__ubx_ref_station_id BIGINT,

  metric__ntrip_connected BIGINT,
  metric__ntrip_send BIGINT,
  metric__ntrip_recv BIGINT,

  metric__lsi_connected BIGINT,
  metric__lsi_acks_missed BIGINT,

  metric__ubx_boot_type BIGINT,
  metric__ubx_runtime BIGINT,

  metric__ubx_sensor_fusion_wt_init BIGINT,
  metric__ubx_sensor_fusion_mnt_alg BIGINT,
  metric__ubx_sensor_fusion_ins_init BIGINT,
  metric__ubx_sensor_fusion_imu_init BIGINT,

  metric__sensor_fusion_state BIGINT,

  metric__uwb_num_sats BIGINT,

  metric__uwb_sat_1_addr BIGINT,
  metric__uwb_sat_1_rssi BIGINT,
  metric__uwb_sat_1_nlos BIGINT,
  metric__uwb_sat_2_addr BIGINT,
  metric__uwb_sat_2_rssi BIGINT,
  metric__uwb_sat_2_nlos BIGINT,
  metric__uwb_sat_3_addr BIGINT,
  metric__uwb_sat_3_rssi BIGINT,
  metric__uwb_sat_3_nlos BIGINT,
  metric__uwb_sat_4_addr BIGINT,
  metric__uwb_sat_4_rssi BIGINT,
  metric__uwb_sat_4_nlos BIGINT,
  metric__uwb_sat_5_addr BIGINT,
  metric__uwb_sat_5_rssi BIGINT,
  metric__uwb_sat_5_nlos BIGINT,
  metric__uwb_sat_6_addr BIGINT,
  metric__uwb_sat_6_rssi BIGINT,
  metric__uwb_sat_6_nlos BIGINT,

  metric__cpu_load_percent_cpu_0 BIGINT,
  metric__cpu_load_percent_cpu_1 BIGINT,

  metric__uptime_seconds BIGINT,
  metric__sleep_manager_state BIGINT,
  metric__last_power_cut_unix_seconds BIGINT,
  metric__mileage_mm BIGINT,

  metric__reset_count_poweron BIGINT,
  metric__reset_count_software BIGINT,
  metric__reset_count_panic BIGINT,
  metric__reset_count_wd BIGINT,
  metric__reset_count_brownout BIGINT,
  metric__reset_count_pwrglitch BIGINT,
  metric__reset_count_unknown BIGINT,

  metric__uwb_tacho_speed DOUBLE PRECISION,
  metric__uwb_pan_id BIGINT
);

CREATE INDEX IF NOT EXISTS rawpos_devicetime_idx ON rawpos (devicetime);
CREATE INDEX IF NOT EXISTS rawpos_tracelet_devicetime_idx ON rawpos (tracelet_id, devicetime);

