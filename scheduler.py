from aegis.orchestrator import run_scheduler


def main() -> None:
    run_scheduler(hour=7, minute=0, symbol="SPY")


if __name__ == "__main__":
    main()
