#!/usr/bin/env python3
"""Queue Worker - Processes queued messages and scheduled sends.

Run: python3 -m communications_department.workers.queue_worker
Or via PM2: pm2 start queue_worker.py --name hermes-worker --interpreter python3
"""
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from communications_department.engine.database import CommsDB
from communications_department.engine.sms import SMSEngine
from communications_department.engine.email_engine import EmailEngine
from communications_department.engine.voice import VoiceEngine
from communications_department.engine.router import MessageRouter
from communications_department.engine.scheduler import MessageScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [HERMES-WORKER] %(message)s",
)
log = logging.getLogger("hermes.worker")

POLL_INTERVAL = 10  # seconds


def run_worker():
    """Main worker loop - processes queues and scheduled messages."""
    db = CommsDB()
    sms = SMSEngine(db=db)
    email_eng = EmailEngine(db=db)
    voice = VoiceEngine(db=db)
    router = MessageRouter(db=db, sms_engine=sms, email_engine=email_eng, voice_engine=voice)
    scheduler = MessageScheduler(db=db, router=router)

    log.info("HERMES queue worker started. Polling every %ds", POLL_INTERVAL)

    while True:
        try:
            # Process queued messages
            queue_results = router.process_queue(batch_size=20)
            if queue_results:
                log.info("Processed %d queued messages", len(queue_results))

            # Process scheduled messages
            sched_results = scheduler.process_due()
            if sched_results:
                log.info("Processed %d scheduled messages", len(sched_results))

        except Exception as e:
            log.error("Worker error: %s", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_worker()
