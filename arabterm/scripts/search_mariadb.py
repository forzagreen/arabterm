import argparse
import json

from sqlalchemy import text

from arabterm.mariadb_models import get_mariadb_connection


def search_terms_mariadb(session, query_text) -> list[dict]:
    return (
        session.execute(
            text("""
        SELECT
            t.*,
            d.name_arabic as dictionary_name_arabic,
            d.wikidata_id as dictionary_wikidata_id,
            MATCH(t.arabic, t.english, t.french, t.description)
            AGAINST(:query IN NATURAL LANGUAGE MODE) as relevance
        FROM term t
        JOIN dictionary d ON t.dictionary_id = d.id
        WHERE MATCH(t.arabic, t.english, t.french, t.description)
        AGAINST(:query IN NATURAL LANGUAGE MODE)
        ORDER BY relevance DESC
    """),
            {"query": query_text},
        )
        .mappings()
        .all()
    )


def main():
    parser = argparse.ArgumentParser(
        description="Search a term in MariaDB. Uses full-text search."
    )

    parser.add_argument("term", help="The term to search for")
    args = parser.parse_args()

    with get_mariadb_connection() as mariadb_session:
        results = search_terms_mariadb(mariadb_session, args.term)
        results = [dict(row) for row in results]
        for row in results:
            keys = list(row.keys())
            for key in keys:
                if key not in ["id", "arabic", "english", "french", "dictionary_name_arabic"]:
                    row.pop(key)

        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
