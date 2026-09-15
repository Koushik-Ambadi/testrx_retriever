"""Compatibility CLI; use :mod:`testrx_retriever.workflows.reference_run`."""

from .workflows.reference_run import *  # noqa: F401,F403
from .workflows.reference_run import main


if __name__ == "__main__":
    raise SystemExit(main())
