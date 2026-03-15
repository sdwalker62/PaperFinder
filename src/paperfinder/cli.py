"""CLI entry point for PaperFinder."""

from __future__ import annotations

import argparse
import logging
import sys

from paperfinder import __version__


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="paperfinder",
        description="Automated ML/AI paper & blog discovery, summarization, and delivery.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command")

    # ── run ──────────────────────────────────────────────────────
    run_parser = sub.add_parser("run", help="Run the pipeline once and exit")
    run_parser.add_argument(
        "--lookback-days",
        type=int,
        default=None,
        metavar="N",
        help="Override scraping.lookback_days (useful for backfills)",
    )
    run_parser.add_argument(
        "--skip-delivery",
        action="store_true",
        help="Skip email and Discord delivery (for backfills)",
    )

    # ── serve ────────────────────────────────────────────────────
    sub.add_parser("serve", help="Start the daily scheduler")

    # ── scrape-only ─────────────────────────────────────────────
    sub.add_parser("scrape-only", help="Scrape sources without LLM/delivery (for debugging)")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.command == "run":
        from paperfinder.pipeline import run_pipeline

        run_pipeline(
            lookback_days=args.lookback_days,
            skip_delivery=args.skip_delivery,
        )
    elif args.command == "serve":
        from paperfinder.scheduler import start_scheduler

        start_scheduler()
    elif args.command == "scrape-only":
        from paperfinder.config import load_settings, load_sources
        from paperfinder.scrapers import scrape_all

        settings = load_settings()
        sources = load_sources()
        papers = scrape_all(sources, settings.scraping, settings.scraping.lookback_days)
        for p in papers:
            print(f"[{p.source_name}] {p.title}")
            print(f"  → {p.url}")
        print(f"\nTotal: {len(papers)} papers/posts")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
