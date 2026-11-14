"""CI entry point for the order integration checks."""
from acceptance import main as run_acceptance

if __name__ == "__main__":
    raise SystemExit(run_acceptance())
