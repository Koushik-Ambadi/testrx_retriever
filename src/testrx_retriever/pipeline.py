"""Compatibility CLI; use :mod:`testrx_retriever.workflows.model_comparison`."""

from .workflows.model_comparison import *  # noqa: F401,F403
from .workflows.model_comparison import main


if __name__ == "__main__":
    raise SystemExit(main())
