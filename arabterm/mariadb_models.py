import datetime
import os
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Dictionary(Base):
    __tablename__ = "dictionary"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name_arabic: Mapped[Optional[str]] = mapped_column(String(255))
    name_english: Mapped[Optional[str]] = mapped_column(String(255))
    name_french: Mapped[Optional[str]] = mapped_column(String(255))
    nbr_entries: Mapped[Optional[int]] = mapped_column(Integer)
    name_tech: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    wikidata_id: Mapped[Optional[str]] = mapped_column(String(255))
    dict_type: Mapped[Optional[str]] = mapped_column(String(255))
    tier: Mapped[Optional[int]] = mapped_column(Integer)
    # Text, not String(255): a URL into a multi-volume item names the volume's
    # file, percent-encoded (dstt_1's is 292 characters).
    archive_org_url: Mapped[Optional[str]] = mapped_column(Text)
    page_offset: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )

    term: Mapped[List["Term"]] = relationship("Term", back_populates="dictionary")
    domains: Mapped[List["Domain"]] = relationship(
        "Domain",
        secondary="dictionary_domain",
        back_populates="dictionaries",
        order_by="Domain.id",
    )


class Domain(Base):
    """A subject a dictionary is about: one value of "main subject" (P921) on
    the dictionaries' Wikidata items, under a short name fit for a tag
    («رياضيات», where the Wikidata item is «مصطلحات الرياضيات»)."""

    __tablename__ = "domain"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name_tech: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name_arabic: Mapped[str] = mapped_column(String(255), nullable=False)
    name_english: Mapped[Optional[str]] = mapped_column(String(255))
    name_french: Mapped[Optional[str]] = mapped_column(String(255))
    # The Wikidata item used as the P921 value, e.g. Q66785817.
    wikidata_id: Mapped[Optional[str]] = mapped_column(String(255))

    dictionaries: Mapped[List["Dictionary"]] = relationship(
        "Dictionary", secondary="dictionary_domain", back_populates="domains"
    )


class DictionaryDomain(Base):
    """A dictionary has one domain or several (mathematics and astronomy)."""

    __tablename__ = "dictionary_domain"
    __table_args__ = {"mysql_engine": "InnoDB"}

    dictionary_id: Mapped[int] = mapped_column(
        ForeignKey("dictionary.id"), primary_key=True
    )
    domain_id: Mapped[int] = mapped_column(ForeignKey("domain.id"), primary_key=True)


class Term(Base):
    __tablename__ = "term"
    __table_args__ = (
        Index(
            "idx_term_fulltext",
            "arabic",
            "english",
            "french",
            "description",
            mysql_prefix="FULLTEXT",
        ),
        {"mysql_engine": "InnoDB"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    arabic: Mapped[Optional[str]] = mapped_column(String(255))
    english: Mapped[Optional[str]] = mapped_column(String(255))
    french: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"))
    page: Mapped[Optional[int]] = mapped_column(Integer)
    uri: Mapped[Optional[str]] = mapped_column(String(255))

    dictionary: Mapped["Dictionary"] = relationship("Dictionary", back_populates="term")


def get_mariadb_connection():
    """Create MariaDB connection"""
    MARIADB_URL = os.environ["MARIADB_URL"]
    engine = create_engine(MARIADB_URL)
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    return Session(engine)
