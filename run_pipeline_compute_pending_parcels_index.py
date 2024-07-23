import argparse

from cgm.logger import get_logger
from cgm.pipelines.compute_pending_parcels_index import compute_pending_parcels_index

log = get_logger()


def valid_int(s):
    try:
        return int(s)
    except ValueError:
        msg = f"Not a valid int: '{s}'."
        raise argparse.ArgumentTypeError(msg)


def valid_float(s):
    try:
        return float(s)
    except ValueError:
        msg = f"Not a valid float: '{s}'."
        raise argparse.ArgumentTypeError(msg)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--max',
                        required=False,
                        type=valid_int,
                        default=None,
                        help="Max number of parcels index computations, if none provided, all will be computed.")

    parser.add_argument('--precision',
                        required=False,
                        type=valid_float,
                        default=0.0001,
                        help="Spacial precision for index computations.")

    args = vars(parser.parse_args())

    compute_all = False if args['max'] else True

    # Launch pipeline
    compute_pending_parcels_index(resolution=args["precision"],
                                  max_parcels_to_compute=args["max"],
                                  compute_all=compute_all)


if __name__ == "__main__":
    main()
