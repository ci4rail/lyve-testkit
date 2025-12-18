import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


EASYPLAN_HEADER = {
    "buildingName": "CMMC",
    "deviceName": "Klaus-Laptop2",
    "levelName": "carport-test",
    "configName": "default",
    "siteId": "cc11",
    "version": 4.0,
}


def iso_to_epoch_ms(ts: Optional[str]) -> Optional[int]:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None
    ms = int(dt.timestamp() * 1000)
    # Some logs contain placeholder epoch timestamps (1970-01-01...).
    # Treat them as missing to avoid creating "1970" chunks/files.
    if ms <= 0:
        return None
    return ms


def parse_time_arg(value: Optional[str]) -> Optional[int]:
    """Parse a CLI time argument into epoch milliseconds.

    Supports:
    - ISO 8601 strings (e.g. 2025-12-17T13:37:29Z or with offset)
    - epoch milliseconds (integer)
    """
    if value is None or value == "":
        return None
    v = value.strip()
    if v.isdigit():
        try:
            return int(v)
        except ValueError:
            return None

    try:
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None

    # If the string has no timezone info, interpret it as local time.
    if dt.tzinfo is None:
        local_tz = datetime.now().astimezone().tzinfo
        dt = dt.replace(tzinfo=local_tz)

    return int(dt.astimezone(timezone.utc).timestamp() * 1000)


def filter_entries_by_time_range(
    raw_entries: List[Dict[str, Any]],
    start_ms: Optional[int],
    end_ms: Optional[int],
) -> List[Dict[str, Any]]:
    if start_ms is None and end_ms is None:
        return raw_entries

    filtered: List[Dict[str, Any]] = []
    for entry in raw_entries:
        ts_ms = iso_to_epoch_ms((entry or {}).get("delivery_ts"))
        if ts_ms is None:
            continue
        if start_ms is not None and ts_ms < start_ms:
            continue
        if end_ms is not None and ts_ms > end_ms:
            continue
        filtered.append(entry)
    return filtered


def epoch_ms_to_filename_local(ms: Optional[int]) -> str:
    if ms is None:
        return "na"
    dt = datetime.fromtimestamp(ms / 1000).astimezone()
    return dt.strftime("%Y%m%d_%H%M%S")


def chunk_time_range_ms(chunk: Dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
    positions = chunk.get("positions") or {}
    timestamps: List[int] = []
    for pos_list in positions.values():
        for pos in pos_list or []:
            ts = (pos or {}).get("timeStamp")
            if isinstance(ts, int):
                timestamps.append(ts)

    if not timestamps:
        return None, None
    return min(timestamps), max(timestamps)


def build_position(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    tracelet_id = entry.get("tracelet_id")
    if not tracelet_id:
        return None

    location = entry.get("location") or {}
    gnss = location.get("gnss") or {}
    uwb = location.get("uwb") or {}
    fused = location.get("fused") or {}

    timestamp_ms = iso_to_epoch_ms(entry.get("delivery_ts"))

    return {
        "tracelet_id": tracelet_id,
        "timeStamp": timestamp_ms,
        "gnssPosition": {
            "latitude": gnss.get("latitude"),
            "longitude": gnss.get("longitude"),
            "altitude": gnss.get("altitude"),
            "eph": gnss.get("eph"),
            "epv": gnss.get("epv"),
            "fixType": gnss.get("fix_type"),
            "headMotion": gnss.get("head_motion"),
            "headVehicle": gnss.get("head_vehicle"),
            "groundSpeed": gnss.get("ground_speed"),
        },
        "fusedPosition": {
            "latitude": fused.get("latitude"),
            "longitude": fused.get("longitude"),
            "eph": fused.get("eph"),
            "headMotion": fused.get("head_motion"),
            "headVehicle": fused.get("head_vehicle"),
            "altitude": fused.get("altitude"),
            "groundSpeed": fused.get("ground_speed"),
        },
        "uwbPosition": {
            "siteId": str(uwb["site_id"]) if "site_id" in uwb else None,
            "xCoordinate": uwb.get("x"),
            "yCoordinate": uwb.get("y"),
            "zCoordinate": uwb.get("z"),
            "accuracy": uwb.get("eph"),
            "covXx": None,
            "covXy": None,
            "covYy": None,
            "level": EASYPLAN_HEADER["levelName"],
            "signature": int(uwb["location_signature"]) if "location_signature" in uwb else None,
            "fixType": uwb.get("fix_type"),
            "headMotion": uwb.get("head_motion"),
            "headVehicle": uwb.get("head_vehicle"),
            "groundSpeed": uwb.get("ground_speed"),
        },
    }


def convert_entries(raw_entries: List[Dict[str, Any]], chunk_minutes: int) -> List[Dict[str, Any]]:
    positions: Dict[str, List[Dict[str, Any]]] = {}

    for entry in raw_entries:
        pos = build_position(entry)
        if not pos:
            continue

        tracelet_id = pos.pop("tracelet_id")
        positions.setdefault(tracelet_id, []).append(pos)

    # Determine chunking start based on earliest timestamp that exists.
    timestamps = [
        p["timeStamp"] for pos_list in positions.values() for p in pos_list if p.get("timeStamp") is not None
    ]
    if not timestamps or chunk_minutes <= 0:
        return [{"header": EASYPLAN_HEADER, "positions": positions}]

    chunk_ms = chunk_minutes * 60 * 1000
    min_ts = min(timestamps)

    # Bucket each position into a chunk, keeping tracelets separated inside each chunk.
    chunk_map: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}
    for tracelet_id, pos_list in positions.items():
        for pos in sorted(pos_list, key=lambda p: p.get("timeStamp") or 0):
            ts = pos.get("timeStamp")
            if ts is None:
                continue
            chunk_idx = (ts - min_ts) // chunk_ms
            bucket = chunk_map.setdefault(chunk_idx, {})
            bucket.setdefault(tracelet_id, []).append(pos)

    return [{"header": EASYPLAN_HEADER, "positions": chunk_map[idx]} for idx in sorted(chunk_map.keys())]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Benthos log JSON to Easyplan format."
    )
    parser.add_argument("input", help="Path to Benthos log JSON file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output path for Easyplan JSON (defaults to stdout).",
    )
    parser.add_argument(
        "--chunk-minutes",
        type=int,
        default=10,
        help="Chunk length in minutes (<=0 disables chunking).",
    )
    parser.add_argument(
        "--from",
        dest="from_ts",
        help=(
            "Start time (inclusive). ISO8601 (e.g. 2025-12-17T13:00:00Z or 2025-12-17T13:00:00+01:00); "
            "if no timezone is given, local time is assumed. Also accepts epoch ms."
        ),
    )
    parser.add_argument(
        "--to",
        dest="to_ts",
        help=(
            "End time (inclusive). ISO8601 (e.g. 2025-12-17T14:00:00Z or 2025-12-17T14:00:00+01:00); "
            "if no timezone is given, local time is assumed. Also accepts epoch ms."
        ),
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    with input_path.open("r", encoding="utf-8") as f:
        raw_entries = json.load(f)

    start_ms = parse_time_arg(args.from_ts)
    end_ms = parse_time_arg(args.to_ts)
    if start_ms is not None and end_ms is not None and start_ms > end_ms:
        parser.error("--from must be <= --to")

    raw_entries = filter_entries_by_time_range(raw_entries, start_ms, end_ms)

    chunks = convert_entries(raw_entries, args.chunk_minutes)

    # If a time range was requested, always include start/end in the output filename,
    # even when only a single chunk is produced.
    force_time_suffix = start_ms is not None or end_ms is not None

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = output_path.suffix or ".json"
        stem = output_path.stem
        parent = output_path.parent

        if len(chunks) == 1 and not force_time_suffix:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(chunks[0], f, indent=2)
        else:
            for chunk in chunks:
                chunk_start_ms, chunk_end_ms = chunk_time_range_ms(chunk)
                start_s = epoch_ms_to_filename_local(chunk_start_ms)
                end_s = epoch_ms_to_filename_local(chunk_end_ms)
                part_path = parent / f"{stem}_{start_s}-{end_s}{suffix}"
                with part_path.open("w", encoding="utf-8") as f:
                    json.dump(chunk, f, indent=2)
    else:
        for idx, chunk in enumerate(chunks):
            if idx:
                sys.stdout.write("\n")
            json.dump(chunk, fp=sys.stdout, indent=2)


if __name__ == "__main__":
    main()
