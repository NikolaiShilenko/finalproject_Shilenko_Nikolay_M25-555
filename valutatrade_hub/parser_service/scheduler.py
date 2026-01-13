import logging
import threading
import time

from .config import ParserConfig
from .updater import RatesUpdater

logger = logging.getLogger(__name__)


class RatesScheduler:
    def __init__(self, config: ParserConfig = None):
        self.config = config or ParserConfig()
        self.updater = RatesUpdater(config)
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"Scheduler started with interval {self.config.UPDATE_INTERVAL_MINUTES} min")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_loop(self):
        while self.is_running:
            try:
                logger.info("Scheduled update started")
                self.updater.run_update()
                logger.info("Scheduled update completed")
            except Exception as e:
                logger.error(f"Scheduled update failed: {e}")

            for _ in range(self.config.UPDATE_INTERVAL_MINUTES * 60):
                if not self.is_running:
                    break
                time.sleep(1)
