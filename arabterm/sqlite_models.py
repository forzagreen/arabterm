from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime


class Base(DeclarativeBase):
    pass


class Dictionary(Base):
    __tablename__ = 'dictionary'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_arabic: Mapped[Optional[str]] = mapped_column(String)
    name_english: Mapped[Optional[str]] = mapped_column(String)
    name_french: Mapped[Optional[str]] = mapped_column(String)
    name_german: Mapped[Optional[str]] = mapped_column(String)
    nbr_entries: Mapped[Optional[int]] = mapped_column(Integer)
    name_tech: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    wikidata_id: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    term: Mapped[List['Term']] = relationship('Term', back_populates='dictionary')


class Term(Base):
    __tablename__ = 'term'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    arabic: Mapped[Optional[str]] = mapped_column(String)
    english: Mapped[Optional[str]] = mapped_column(String)
    french: Mapped[Optional[str]] = mapped_column(String)
    german: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey('dictionary.id'))
    page: Mapped[Optional[int]] = mapped_column(Integer)
    uri: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    dictionary: Mapped['Dictionary'] = relationship('Dictionary', back_populates='term')
