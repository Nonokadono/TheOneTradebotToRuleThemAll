from datetime import datetime, timedelta

class SimpleScheduler:
    def __init__(self, interval_seconds: int = 60) -> None:
        self.interval = timedelta(seconds=interval_seconds)
        self.next_run = datetime.utcnow()

    def should_run(self) -> bool:
        now = datetime.utcnow()
        if now >= self.next_run:
            self.next_run = now + self.interval
            return True
        return False
