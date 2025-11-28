import logging

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.db.seeds import seed_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init() -> None:
    db = SessionLocal()
    init_db(db)
    seed_data(db)

def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")

if __name__ == "__main__":
    main()
