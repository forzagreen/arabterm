from sqlalchemy import text

from arabterm.sqlite_models import get_sqlite_connection


def rename_arabterm_prefix(sqlite_session):
    """Rename `arabterm_*` slugs in dictionary.name_tech to `at_*`."""
    try:
        result = sqlite_session.execute(
            text(
                "UPDATE dictionary "
                "SET name_tech = 'at_' || substr(name_tech, length('arabterm_') + 1) "
                "WHERE name_tech LIKE 'arabterm_%'"
            )
        )
        sqlite_session.commit()
        print(f"Updated {result.rowcount} rows.")
    except Exception as e:
        print(f"Error renaming name_tech: {str(e)}")
        sqlite_session.rollback()
        raise


def main():
    print("Renaming arabterm_* -> at_* in SQLite dictionary.name_tech...")
    with get_sqlite_connection() as sqlite_session:
        rename_arabterm_prefix(sqlite_session)


if __name__ == "__main__":
    main()
