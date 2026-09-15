"""Compatibility CLI; use :mod:`testrx_retriever.evaluation.analysis`."""

from .evaluation.analysis import *  # noqa: F401,F403
from .evaluation.analysis import main


if __name__ == "__main__":
    raise SystemExit(main())
