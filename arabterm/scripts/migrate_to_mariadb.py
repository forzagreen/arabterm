import datetime
import sys
from typing import Any, Dict

from sqlalchemy.orm import Session

from arabterm.mariadb_models import Dictionary as DictionaryMariaDB
from arabterm.mariadb_models import Term as TermMariaDB
from arabterm.mariadb_models import get_mariadb_connection
from arabterm.sqlite_models import Dictionary as DictionarySQLite
from arabterm.sqlite_models import Term as TermSQLite
from arabterm.sqlite_models import get_sqlite_connection


def migrate_dictionary(sqlite_dict: DictionarySQLite) -> Dict[str, Any]:
    """Convert SQLite dictionary to MariaDB dictionary data"""
    return {
        "id": sqlite_dict.id,
        "name_arabic": sqlite_dict.name_arabic,
        "name_english": sqlite_dict.name_english,
        "name_french": sqlite_dict.name_french,
        "name_german": sqlite_dict.name_german,
        "nbr_entries": sqlite_dict.nbr_entries,
        "name_tech": sqlite_dict.name_tech,
        "wikidata_id": sqlite_dict.wikidata_id,
        "created_at": sqlite_dict.created_at or datetime.datetime.now(),
        "updated_at": sqlite_dict.updated_at,
    }


def migrate_term(sqlite_term: TermSQLite) -> Dict[str, Any]:
    """Convert SQLite term to MariaDB term data"""
    return {
        "id": sqlite_term.id,
        "arabic": sqlite_term.arabic,
        "english": sqlite_term.english,
        "french": sqlite_term.french,
        "german": sqlite_term.german,
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
        sqlite_terms = sqlite_session.query(TermSQLite).all()
        for sqlite_term in sqlite_terms:
            term_data = migrate_term(sqlite_term)
            mariadb_term = TermMariaDB(**term_data)
            mariadb_session.add(mariadb_term)

        # Commit terms
        mariadb_session.commit()
        print(f"Successfully migrated {len(sqlite_terms)} terms")

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
