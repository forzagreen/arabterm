import datetime
import os
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class Dictionary(Base):
    __tablename__ = "dictionary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_arabic: Mapped[Optional[str]] = mapped_column(String)
    name_english: Mapped[Optional[str]] = mapped_column(String)
    name_french: Mapped[Optional[str]] = mapped_column(String)
    nbr_entries: Mapped[Optional[int]] = mapped_column(Integer)
    name_tech: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    wikidata_id: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, onupdate=utc_now
    )

    term: Mapped[List["Term"]] = relationship("Term", back_populates="dictionary")


class Term(Base):
    __tablename__ = "term"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arabic: Mapped[Optional[str]] = mapped_column(String)
    english: Mapped[Optional[str]] = mapped_column(String)
    french: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"))
    page: Mapped[Optional[int]] = mapped_column(Integer)
    uri: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, onupdate=utc_now
    )

    dictionary: Mapped["Dictionary"] = relationship("Dictionary", back_populates="term")


def get_sqlite_connection():
    """Create SQLite connection"""
    SQLITE_URL = os.environ.get("SQLITE_URL", "sqlite:///arabterm.db")
    engine = create_engine(SQLITE_URL)
    return Session(engine)
