import argparse
from datetime import datetime

from cgm.logger import get_logger
from cgm.database.requests import get_all_rpg_parcels
from cgm.pipelines.request_sentinel_2_data import request_sentinel_2_data

log = get_logger()


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = f"Not a valid date: '{s}'. Expected format: YYYY-MM-DD"
        raise argparse.ArgumentTypeError(msg)


def main():
    parser = argparse.ArgumentParser(description="Process date range.")
    parser.add_argument('--from', required=True, type=valid_date, help="Start date in format YYYY-MM-DD")
    parser.add_argument('--to', required=True, type=valid_date, help="End date in format YYYY-MM-DD")
    args = vars(parser.parse_args())

    # TODO : create groups of parcels that are :
    #   - close / contiguous from each others
    #   - on the same sentinel 2 grid
    # TODO : do pipeline only for a given group (as argument)
    # Get parcels for which we want to request data from collection
    parcels_to_requests = get_all_rpg_parcels()
    log.info("%s parcels uploaded from database", len(parcels_to_requests))

    # Launch pipeline
    request_sentinel_2_data(parcels_to_requests=parcels_to_requests,
                            from_datetime=args["from"],
                            to_datetime=args["to"])


if __name__ == "__main__":
    main()
