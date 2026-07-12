from aegis.orchestrator import run_robot


def main() -> None:
    result = run_robot()
    print("Aegis run complete.")
    print("Approved:", len(result.get("approved", [])))
    print("Rejected:", len(result.get("rejected", [])))


if __name__ == "__main__":
    main()
