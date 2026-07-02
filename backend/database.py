from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import settings

# Create database engine (connects to MySQL)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=settings.DB_CONNECT_ARGS,
)

# Session factory - used to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our models (tables) will inherit from
Base = declarative_base()


def create_database_if_missing():
    """Create the configured MySQL database before connecting to it."""
    if settings.RAW_DATABASE_URL:
        return

    server_engine = create_engine(
        settings.MYSQL_SERVER_URL,
        pool_pre_ping=True,
        connect_args=settings.DB_CONNECT_ARGS,
    )
    database_name = settings.DB_NAME.replace("`", "``")

    try:
        with server_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database_name}`"))
            connection.commit()
    except SQLAlchemyError as exc:
        print(f"Skipping database auto-create: {exc}")
    finally:
        server_engine.dispose()


def get_db():
    """
    Dependency used by FastAPI routes to get a database session,
    and automatically close it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables in the database if they don't already exist.
    Called once when the app starts.
    """
    create_database_if_missing()
    from models import Lead  # noqa: F401 (import so SQLAlchemy registers the model)
    Base.metadata.create_all(bind=engine)
