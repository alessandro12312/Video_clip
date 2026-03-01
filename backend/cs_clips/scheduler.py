import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# TODO togliere i log
def close_contests_job():
    logger.info("Attempting to run 'close_contests' command.")
    try:
        call_command("close_contests")
        logger.info("'close_contests' command executed successfully.")
    except Exception as e:
        logger.error(f"Error running 'close_contests' command: {e}")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        close_contests_job,
        "cron",
        day_of_week="thu",
        hour=11,
        minute=33,
    )
    logger.info(
        "Scheduler started. 'close_contests' job scheduled for Thursday at 11:24."
    )
    scheduler.start()


# def start():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(
#         lambda: call_command('close_contests'),
#         'cron',
#         day_of_week='thu',
#         hour=11,
#         minute=24
#     )
#     scheduler.start()
