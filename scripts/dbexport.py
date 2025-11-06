import psycopg2
import csv
import datetime
import argparse

tool_description = """
This script exports the position data from database to to a CSV file.
"""


def exec_query(host, port, user, password, start_time, end_time, tracelet_id):
    conn = psycopg2.connect(
        host=host, port=port, database="raw_pos", user=user, password=password
    )

    # Step 2: Create a cursor object
    cur = conn.cursor()

    # Construct the SQL query
    query = f"""SELECT devicetime, servertime, fused_latitude, fused_longitude, fused_eph FROM pos WHERE devicetime BETWEEN '{start_time}' AND '{end_time}' AND tracelet_id = '{tracelet_id}' ORDER BY servertime ASC;"""

    # Execute the query
    cur.execute(query)

    # Fetch all the rows
    rows = cur.fetchall()

    # Get the column names
    column_names = [desc[0] for desc in cur.description]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return column_names, rows


def export_csv(rows, column_names, output_filename):
    fields = ["devicetime", "servertime", "flight_time", "fused_latitude", "fused_longitude", "fused_eph"]

    with open(output_filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(fields) # write the header

        devtime_idx = column_names.index(fields[0])
        servertime_idx = column_names.index(fields[1])
        fused_lat_idx = column_names.index(fields[3])
        fused_lon_idx = column_names.index(fields[4])
        fused_eph_idx = column_names.index(fields[5])

        for row in rows:
            devtime = row[devtime_idx]

            flight_time = (row[servertime_idx] - row[devtime_idx]).total_seconds()

            # Format devtime to ISO 8601
            devtime_iso = row[devtime_idx].isoformat()
            servertime_iso = row[servertime_idx].isoformat()

            content = [
                devtime_iso,
                servertime_iso,
                flight_time,
                row[fused_lat_idx],
                row[fused_lon_idx],
                row[fused_eph_idx],
            ]
            writer.writerow(content)

def run(args):
    column_names, rows = exec_query(
        args.host,
        args.port,
        args.user,
        args.password,
        args.start,
        args.end,
        args.tracelet_id,
    )
    export_csv(rows, column_names, args.output)
    print(f"wrote {len(rows)} rows to {args.output}")

def command_line_args_parsing():
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument(
        "--start",
        help="start time in UTC e.g. '2024-03-06 10:00:00'",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--end",
        help="end time in UTC e.g. '2024-03-06 10:00:00'",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--host",
        help="database server host name",
        type=str,
        default="tadpole",
    )
    parser.add_argument(
        "--port",
        help="database server port number",
        type=str,
        default="5432",
    )
    parser.add_argument(
        "--user",
        help="database user name",
        type=str,
        default="user",
    )
    parser.add_argument(
        "--password",
        help="database user password",
        type=str,
        default="password",
    )
    parser.add_argument(
        "--tracelet_id",
        help="tracelet id",
        type=str,
        default="FORKLIFTER-2",
    )
    parser.add_argument(
        "--output",
        help="output filename to write",
        type=str,
        default="raw_pos.csv",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = command_line_args_parsing()
    run(args)
