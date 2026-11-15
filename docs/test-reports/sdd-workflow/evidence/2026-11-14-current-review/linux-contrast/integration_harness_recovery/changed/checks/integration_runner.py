"""CI entry point for the order integration checks."""
if __package__:
    from .acceptance import main as run_acceptance
else:
    from acceptance import main as run_acceptance

if __name__ == "__main__":
    raise SystemExit(run_acceptance())
