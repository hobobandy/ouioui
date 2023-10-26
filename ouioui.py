import argparse
import logging
import ouioui


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="small utility script, and library, to download the IEEE OUI MA-L assignments file, override them if needed, and save them into a SQLite db to query.",
        epilog=f"version {ouioui.version}",
    )
    parser.add_argument(
        "--debug", action="store_true", help="increase verbosity with debug messages"
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        help="configuration file to override default settings",
    )
    group = parser.add_argument_group("actions", "one of these is required")
    mxgroup = group.add_mutually_exclusive_group(required=True)
    mxgroup.add_argument(
        "-q",
        "--query",
        help="OUI prefix to look up (charset: A-Z0-9, others will be removed)",
    )
    mxgroup.add_argument(
        "--update",
        action="store_true",
        help="fetch sources, load custom oui, rebuild database",
    )
    # mxgroup.add_argument(
    #     "--update_custom",
    #     action="store_true",
    #     help="load custom oui, update existing database"
    # )
    mxgroup.add_argument(
        "--package_for_kismet",
        action="store_true",
        help="fetch sources, package as .txt.gz for kismet (ouifile=<path> in kismet_site.conf)",
    )

    args = parser.parse_args()

    o = ouioui.from_args(args)

    if args.update:
        o.update()
    # elif args.update_custom:
    #     o.update_custom()
    elif args.package_for_kismet:
        o.package_for_kismet()
    elif args.query:
        logging.info(o.lookup(args.query))
