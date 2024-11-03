from arabterm.mariadb_models import Base as MariaDBBase
from arabterm.mariadb_models import get_mariadb_connection


def delete_mariadb_data(mariadb_session):
    """Delete all data from MariaDB tables"""
    try:
        MariaDBBase.metadata.drop_all(bind=mariadb_session.bind)
        mariadb_session.commit()
        print("All tables and data deleted from MariaDB.")
    except Exception as e:
        print(f"Error deleting schema and data: {str(e)}")
        mariadb_session.rollback()
        raise


def main():
    # Delete MariaDB data
    print("Deleting MariaDB tables...")
    with get_mariadb_connection() as mariadb_session:
        delete_mariadb_data(mariadb_session)


if __name__ == "__main__":
    main()
