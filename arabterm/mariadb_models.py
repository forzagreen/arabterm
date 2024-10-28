from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime


class Base(DeclarativeBase):
    pass


class Dictionary(Base):
    __tablename__ = 'dictionary'
    __table_args__ = {
        'mysql_engine': 'InnoDB'
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    name_arabic: Mapped[Optional[str]] = mapped_column(String(255))
    name_english: Mapped[Optional[str]] = mapped_column(String(255))
    name_french: Mapped[Optional[str]] = mapped_column(String(255))
    name_german: Mapped[Optional[str]] = mapped_column(String(255))
    nbr_entries: Mapped[Optional[int]] = mapped_column(Integer)
    name_tech: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    wikidata_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    term: Mapped[List['Term']] = relationship('Term', back_populates='dictionary')


class Term(Base):
    __tablename__ = 'term'
    __table_args__ = (
        Index(
            'idx_term_fulltext',
            'arabic', 'english', 'french', 'description',
            mysql_prefix='FULLTEXT'
        ),
        {'mysql_engine': 'InnoDB'}
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    arabic: Mapped[Optional[str]] = mapped_column(String(255))
    english: Mapped[Optional[str]] = mapped_column(String(255))
    french: Mapped[Optional[str]] = mapped_column(String(255))
    german: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    dictionary_id: Mapped[int] = mapped_column(ForeignKey('dictionary.id'))
    page: Mapped[Optional[int]] = mapped_column(Integer)
    uri: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')
    )

    dictionary: Mapped['Dictionary'] = relationship('Dictionary', back_populates='term')
