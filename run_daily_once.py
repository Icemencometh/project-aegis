from aegis.orchestrator import run_daily_once


def main() -> None:
    result = run_daily_once(symbol="SPY")
    print("Daily Aegis run complete.")
    print("Approved:", len(result.get("approved", [])))
    print("Rejected:", len(result.get("rejected", [])))


if __name__ == "__main__":
    main()
