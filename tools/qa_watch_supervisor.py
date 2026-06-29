"""QA WATCH supervisor — auto-restart qa_watch.py nếu die.

Mr.Long lệnh 30/6: chặn vector "qa_watch loop die silent" — em gap 2h45
overnight không restart, 92+ iter VIOLATION không ai catch.

Pattern:
    while True:
        launch qa_watch.py subprocess
        wait until exit
        log "[WATCHDOG] qa_watch exited code X, restart in 5s"
        sleep 5
        restart

Usage:
    python tools/qa_watch_supervisor.py            # foreground (CMD test)
    nohup python tools/qa_watch_supervisor.py &    # background daemon
    schtasks /create ... /sc onlogon ...           # Windows auto-start logon

Self-protection:
    Log mỗi restart vào runtime/realtime_logs/qa_watch_supervisor.log
    + PING [INFO] log_ping.py để CMD LEAD biết
    Mr.Long check log nếu restart loop fail.

Stop:
    Ctrl+C (foreground) OR Stop-Process supervisor PID
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
QA_WATCH = SVHMP / "tools" / "qa_watch.py"
LOG = SVHMP / "runtime" / "realtime_logs" / "qa_watch_supervisor.log"
QA_LOG = SVHMP / "runtime" / "realtime_logs" / "qa_watch.log"
LOG_PING = SVHMP / "tools" / "log_ping.py"

RESTART_DELAY_S = 5
MAX_RESTARTS_PER_HOUR = 12  # circuit-breaker để không infinite loop nếu qa_watch crash ngay


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(exist_ok=True, parents=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def ping_log(category, msg):
    try:
        subprocess.run(
            ["python", str(LOG_PING), category, msg],
            capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=10,
        )
    except Exception:
        pass


def main():
    log("=== SUPERVISOR started ===")
    log(f"Target: {QA_WATCH}")
    log(f"Log: {LOG}")
    log(f"qa_watch log: {QA_LOG}")
    ping_log("INFO", "CMD LEAD qa_watch_supervisor started — auto-restart nếu die")

    restart_count = 0
    restart_window_start = time.time()

    while True:
        # Circuit breaker check
        now = time.time()
        if now - restart_window_start > 3600:
            restart_window_start = now
            restart_count = 0
        if restart_count >= MAX_RESTARTS_PER_HOUR:
            log(f"!!! CIRCUIT BREAKER: {MAX_RESTARTS_PER_HOUR} restarts in 1h — STOP")
            ping_log("VIOLATION", f"qa_watch_supervisor CIRCUIT BREAKER trip — qa_watch crash >12 times/hour. Mr.Long check qa_watch.log root cause.")
            return 1

        log(f"Launching qa_watch.py (restart #{restart_count + 1} this hour)")
        try:
            proc = subprocess.Popen(
                [sys.executable, str(QA_WATCH)],
                stdout=open(QA_LOG, "a", encoding="utf-8"),
                stderr=subprocess.STDOUT,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            log(f"qa_watch PID {proc.pid}")
            code = proc.wait()
        except KeyboardInterrupt:
            log("Ctrl+C — stopping supervisor")
            if proc and proc.poll() is None:
                proc.terminate()
            return 0
        except Exception as e:
            log(f"!!! Launch error: {e}")
            time.sleep(RESTART_DELAY_S)
            restart_count += 1
            continue

        log(f"qa_watch exited code {code}, restart in {RESTART_DELAY_S}s")
        ping_log("INFO", f"qa_watch exited code {code} — supervisor restart in 5s")
        restart_count += 1
        time.sleep(RESTART_DELAY_S)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("=== SUPERVISOR stopped ===")
        sys.exit(0)
