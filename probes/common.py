"""Shared helpers for the THROWAWAY MT5 farm spike. Never prints credentials."""
import json, os, threading, time
from dataclasses import dataclass
from typing import Callable, Optional

RESULTS_PATH = "/var/empty/results.jsonl"


@dataclass(frozen=True)
class Account:
    label: str
    login: int
    server: str
    investor: str
    master: Optional[str] = None


def load_accounts(raw: str) -> list:
    accounts = []
    for item in json.loads(raw):
        missing = {"label", "login", "server", "investor"} - set(item)
        if missing:
            raise ValueError(f"account entry missing {sorted(missing)}")
        accounts.append(Account(item["label"], int(item["login"]), item["server"], item["investor"], item.get("master")))
    return accounts


def redact(text: str, secrets: list) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, "***")
    return text


class CallTimeout(Exception):
    pass


def timed_call(fn: Callable[[], object], timeout_s: float):
    """Runs fn in a daemon thread; a hung MT5 IPC call can't block the probe forever."""
    box = {}

    def run():
        try:
            box["value"] = fn()
        except BaseException as error:  # reported to the caller below
            box["error"] = error

    start = time.monotonic()
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout_s)
    seconds = time.monotonic() - start
    if thread.is_alive():
        raise CallTimeout(f"call exceeded {timeout_s}s")
    if "error" in box:
        raise box["error"]
    return box.get("value"), seconds


def emit(probe: str, **fields) -> None:
    line = json.dumps({"probe": probe, **fields}, default=str)
    print(f"[result] {line}", flush=True)
    with open(os.environ.get("SPIKE_RESULTS", RESULTS_PATH), "a") as f:
        f.write(line + "\n")
