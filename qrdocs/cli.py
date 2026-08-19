import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="qrdocs",
        description="Self-hosted QR-based asset documentation system",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List documentation entries")

    search_parser = subparsers.add_parser(
        "search",
        help="Search documentation entries",
    )
    search_parser.add_argument(
        "terms",
        nargs="+",
        help="One or more search terms",
    )

    args = parser.parse_args()

    if args.command == "list":
        print("List command not implemented yet.")

    elif args.command == "search":
        print(f"Search terms: {' '.join(args.terms)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
