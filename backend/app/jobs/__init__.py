"""Scheduled jobs for NOVI.

Each module here is runnable with ``python -m app.jobs.<name>`` from ``backend/``
and is designed to be invoked by cron (or any external scheduler) — no in-process
scheduler dependency is required.
"""
