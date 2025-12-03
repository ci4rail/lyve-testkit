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
    return int(dt.timestamp() * 1000)


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
    args = parser.parse_args()

    input_path = Path(args.input)
    with input_path.open("r", encoding="utf-8") as f:
        raw_entries = json.load(f)

    chunks = convert_entries(raw_entries, args.chunk_minutes)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        suffix = output_path.suffix or ".json"
        stem = output_path.stem
        parent = output_path.parent

        if len(chunks) == 1:
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(chunks[0], f, indent=2)
        else:
            for idx, chunk in enumerate(chunks, start=1):
                part_path = parent / f"{stem}_part{idx:02d}{suffix}"
                with part_path.open("w", encoding="utf-8") as f:
                    json.dump(chunk, f, indent=2)
    else:
        for idx, chunk in enumerate(chunks):
            if idx:
                sys.stdout.write("\n")
            json.dump(chunk, fp=sys.stdout, indent=2)


if __name__ == "__main__":
    main()
