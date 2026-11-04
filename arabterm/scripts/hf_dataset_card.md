---
language:
- ar
- en
- fr
license: cc-by-4.0
pretty_name: arabterm — Arabic/English/French terminology dictionaries
tags:
- arabic
- terminology
- dictionary
- glossary
- translation
- multilingual
- wikipedia
task_categories:
- translation
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files: data/terms.parquet
- config_name: dictionaries
  data_files: data/dictionaries.parquet
---

# arabterm — Arabic/English/French terminology dictionaries

<div dir="rtl">

**معاجم المصطلحات العربية**: $n_terms مصطلحًا من $n_dictionaries معجمًا بالعربية والإنجليزية والفرنسية، جُمعت من معاجم المنظمة العربية للتربية والثقافة والعلوم (الألكسو) وموقع arabterm.org ومجمع الملك سلمان العالمي للغة العربية ومجمع اللغة العربية بدمشق ومكتبة لبنان ناشرون وغيرها. هذه هي قاعدة البيانات التي يعتمد عليها [مسرد الويكي](https://wikitermbase.toolforge.org/)، أداة توحيد المصطلحات في ويكيبيديا العربية.

</div>

**$n_terms terms** from **$n_dictionaries dictionaries**, each giving the Arabic term with its English and/or French equivalent, often a description, and for paper dictionaries the printed page number, so that every entry can be cited and checked against the scan. The dictionaries come from ALECSO (the Arab League Educational, Cultural and Scientific Organization), [arabterm.org](https://www.arabterm.org/), the King Salman Global Academy for Arabic Language (KSAA), the Arabic Language Academy of Damascus, Librairie du Liban and other publishers; each one is a Wikidata item.

This is the data behind [Wikitermbase](https://wikitermbase.toolforge.org/) (مسرد الويكي), the terminology search tool of Arabic Wikipedia, and is maintained on GitHub at [forzagreen/arabterm](https://github.com/forzagreen/arabterm), where every dictionary is also browsable at <https://forzagreen.github.io/arabterm/>.

## Loading

```python
from datasets import load_dataset

terms = load_dataset("forzagreen/arabterm")  # $n_terms rows
dictionaries = load_dataset(
    "forzagreen/arabterm", "dictionaries"
)  # $n_dictionaries rows

water = terms["train"].filter(lambda t: t["dictionary"] == "at_water_engineering")
```

Or straight from Parquet, with pandas, polars or DuckDB:

```python
import pandas as pd

terms = pd.read_parquet("hf://datasets/forzagreen/arabterm/data/terms.parquet")
```

## Data

### `terms` (default config, `data/terms.parquet`)

One row per term. Every term has an English value and an Arabic one, with two exceptions: the general dictionary `al_mawrid_al_hadeeth` is English-to-Arabic, so its rows have an English headword and the Arabic definition in `description` with `arabic` empty; and a few dozen rows, listed in the repository's validation baseline, are missing one of the two. French and the description are present where the source dictionary gives them.

| Column | Type | Description |
|:---|:---|:---|
| `id` | int64 | Term id, stable across releases |
| `arabic` | string | Term in Arabic |
| `english` | string | Term in English |
| `french` | string | Term in French |
| `description` | string | Definition or note, usually in Arabic |
| `dictionary_id` | int64 | `dictionaries.id` |
| `dictionary` | string | `dictionaries.name_tech`, the dictionary's slug (joined in for convenience) |
| `page` | int64 | Printed page in the source dictionary, if it is a paper one |
| `uri` | string | Source URL of the entry, if the dictionary is online |
| `created_at` | timestamp | When the row was added (UTC) |
| `updated_at` | timestamp | When the row was last edited (UTC), null if never |

### `dictionaries` (config `dictionaries`, `data/dictionaries.parquet`)

One row per dictionary.

| Column | Type | Description |
|:---|:---|:---|
| `id` | int64 | Dictionary id |
| `name_tech` | string | Slug, unique; the value of `terms.dictionary` |
| `name_arabic` | string | Title in Arabic |
| `name_english` | string | Title in English |
| `name_french` | string | Title in French |
| `nbr_entries` | int64 | Number of terms |
| `dict_type` | string | `terminology` (a specialised dictionary), `thesaurus` (a term list or thesaurus: the ALECSO glossaries, AGROVOC, Electropedia, Arabeyes) or `language` (a general dictionary) |
| `tier` | int64 | Editorial ranking, 1 (most authoritative) to 5 |
| `wikidata_id` | string | Wikidata item of the dictionary, e.g. `Q141137252` |
| `archive_org_url` | string | Scan of the paper dictionary on archive.org (`https://archive.org/details/<item>`), as in Wikidata's P953 |
| `page_offset` | int64 | Printed page `p` is page `p + page_offset` of the scan (Wikidata's P8330) |
| `created_at` | timestamp | When the dictionary was added (UTC) |
| `updated_at` | timestamp | When its row was last edited (UTC), null if never |

For a term on printed page `p` of a dictionary with a scan, the page is at `<archive_org_url>/page/n<p + page_offset - 1>/mode/1up`; this is the link Wikitermbase and the Cite Q module on Arabic Wikipedia build.

## Dictionaries

Most recently added first.

$dictionaries_table

## Source and updates

The canonical data is the SQLite database `arabterm.db` in [forzagreen/arabterm](https://github.com/forzagreen/arabterm), where additions and corrections are made through pull requests and validated in CI. This dataset is regenerated from it automatically whenever the database changes on `main`; the files here were exported from commit $exported_from on $exported_on.

The project started in 2022 as an extraction of the multilingual technical dictionaries of [arabterm.org](https://www.arabterm.org/), and has since grown to include the ALECSO glossaries and dictionaries from the KSAA, the Arabic Language Academy of Damascus, Librairie du Liban and other publishers.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please credit *arabterm* (<https://github.com/forzagreen/arabterm>) and the dictionary the terms come from, which the `dictionary` column and the table above identify.
