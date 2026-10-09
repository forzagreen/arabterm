import datetime
import sys
from typing import Any, Dict

from sqlalchemy import Row, func, insert, null, select, text
from sqlalchemy.orm import Session

from arabterm.mariadb_models import Dictionary as DictionaryMariaDB
from arabterm.mariadb_models import Term as TermMariaDB
from arabterm.mariadb_models import get_mariadb_connection
from arabterm.sqlite_models import Dictionary as DictionarySQLite
from arabterm.sqlite_models import Term as TermSQLite
from arabterm.sqlite_models import get_sqlite_connection

# Terms are copied in batches of this many rows, one transaction per batch.
# Loading the whole table as ORM objects and committing it in one transaction
# takes gigabytes on both sides, which is enough to take a small machine down.
BATCH_SIZE = 2000


def migrate_dictionary(sqlite_dict: DictionarySQLite) -> Dict[str, Any]:
    """Convert SQLite dictionary to MariaDB dictionary data"""
    return {
        "id": sqlite_dict.id,
        "name_arabic": sqlite_dict.name_arabic,
        "name_english": sqlite_dict.name_english,
        "name_french": sqlite_dict.name_french,
        "nbr_entries": sqlite_dict.nbr_entries,
        "name_tech": sqlite_dict.name_tech,
        "wikidata_id": sqlite_dict.wikidata_id,
        "dict_type": sqlite_dict.dict_type,
        "tier": sqlite_dict.tier,
        "created_at": sqlite_dict.created_at or datetime.datetime.now(),
        # A plain `None` here is indistinguishable to SQLAlchemy from "no value
        # given" and gets silently dropped from the INSERT, letting MariaDB's
        # `DEFAULT CURRENT_TIMESTAMP` stamp the row with now() on every re-run.
        # `null()` forces an explicit SQL NULL to be written instead.
        "updated_at": sqlite_dict.updated_at if sqlite_dict.updated_at is not None else null(),
    }


def migrate_term(sqlite_term: Row) -> Dict[str, Any]:
    """Convert SQLite term to MariaDB term data"""
    return {
        "id": sqlite_term.id,
        "arabic": sqlite_term.arabic,
        "english": sqlite_term.english,
        "french": sqlite_term.french,
        "description": sqlite_term.description,
        "dictionary_id": sqlite_term.dictionary_id,
        "page": sqlite_term.page,
        "uri": sqlite_term.uri,
    }


def migrate_data(sqlite_session: Session, mariadb_session: Session):
    """Migrate all data from SQLite to MariaDB"""
    try:
        # Migrate dictionaries
        print("Migrating dictionaries...")
        sqlite_dicts = sqlite_session.query(DictionarySQLite).all()
        for sqlite_dict in sqlite_dicts:
            dict_data = migrate_dictionary(sqlite_dict)
            mariadb_dict = DictionaryMariaDB(**dict_data)
            mariadb_session.add(mariadb_dict)

        # Commit dictionaries first to avoid foreign key issues
        mariadb_session.commit()
        print(f"Successfully migrated {len(sqlite_dicts)} dictionaries")

        # Migrate terms
        print("Migrating terms...")
        # The FULLTEXT index is built after the load: indexing all the rows in
        # one pass is much faster than updating the index on every insert.
        fulltext_index = next(
            index
            for index in TermMariaDB.__table__.indexes
            if index.name == "idx_term_fulltext"
        )
        fulltext_index.drop(mariadb_session.connection(), checkfirst=True)
        # Dropping the index leaves InnoDB's hidden FTS_DOC_ID column behind,
        # and rows loaded with it are not found by an index built afterwards:
        # every search comes back empty. Rebuilding the table removes it.
        mariadb_session.execute(text("ALTER TABLE term FORCE"))

        nbr_terms = 0
        # Plain rows on both sides, not ORM objects. On the MariaDB side this
        # matters: an ORM insert leaves the NULL columns out of the statement,
        # so a batch falls apart into one small INSERT per run of rows that
        # have the same columns set. On the table it is one INSERT per batch.
        batches = sqlite_session.execute(
            select(TermSQLite.__table__)
            .order_by(TermSQLite.id)
            .execution_options(yield_per=BATCH_SIZE)
        ).partitions()
        for sqlite_terms in batches:
            mariadb_session.execute(
                insert(TermMariaDB.__table__),
                [migrate_term(t) for t in sqlite_terms],
            )
            mariadb_session.commit()
            nbr_terms += len(sqlite_terms)
            if nbr_terms % (BATCH_SIZE * 50) == 0:
                print(f"  {nbr_terms} terms...", flush=True)

        print("Building the full-text index...", flush=True)
        fulltext_index.create(mariadb_session.connection())

        # The copy is no longer a single transaction, so check that it is whole
        nbr_mariadb_terms = mariadb_session.scalar(
            select(func.count()).select_from(TermMariaDB)
        )
        if nbr_mariadb_terms != nbr_terms:
            raise RuntimeError(
                f"MariaDB has {nbr_mariadb_terms} terms, expected {nbr_terms}"
                " — run `make delete_mariadb` and migrate again"
            )
        print(f"Successfully migrated {nbr_terms} terms")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        mariadb_session.rollback()
        raise


def main():
    print("Starting migration from SQLite to MariaDB...")

    try:
        sqlite_session = get_sqlite_connection()
        mariadb_session = get_mariadb_connection()

        migrate_data(sqlite_session, mariadb_session)

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        sqlite_session.close()
        mariadb_session.close()


if __name__ == "__main__":
    main()
