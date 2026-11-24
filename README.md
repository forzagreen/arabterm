# arabterm

[![Dataset on Hugging Face](https://huggingface.co/datasets/huggingface/badges/resolve/main/dataset-on-hf-md.svg)](https://huggingface.co/datasets/forzagreen/arabterm)
[![License: CC BY 4.0](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey.svg)](LICENSE)
[![Validate the database](https://github.com/forzagreen/arabterm/actions/workflows/validate-db.yml/badge.svg)](https://github.com/forzagreen/arabterm/actions/workflows/validate-db.yml)
[![Website](https://img.shields.io/badge/website-forzagreen.github.io%2Farabterm-blue)](https://forzagreen.github.io/arabterm/)

This repository is a collection of Arabic/English/French multilingual dictionaries. It serves as the primary data source for [Wiki Term Base](https://wikitermbase.toolforge.org/), a tool designed to standardize terminology used on Arabic Wikipedia and accelerate vocabulary translation.

The dictionaries are available as an [SQLite](https://www.sqlite.org/) database ([arabterm.db.gz](arabterm.db.gz) — gunzip it, or run `make db`), as SQL dumps for SQLite and MariaDB in the [db/](db/) folder, and as Parquet on Hugging Face: [forzagreen/arabterm](https://huggingface.co/datasets/forzagreen/arabterm) (`load_dataset("forzagreen/arabterm")`).

The data is licensed under [CC BY 4.0](LICENSE).


  - [SQLite database](#sqlite-database)
  - [Hugging Face dataset](#hugging-face-dataset)
  - [Dictionaries](#dictionaries)
  - [Website](#website)
  - [Generating database dumps](#generating-database-dumps)
  - [History](#history)
  - [Citation](#citation)
  - [References](#references)


## SQLite database

The full extract is in the SQLite database file [arabterm.db.gz](arabterm.db.gz). It is committed compressed because the database is past GitHub's 100 MiB per-file limit; `gunzip arabterm.db.gz` or `make db` gives you `arabterm.db` to open in any SQLite client.

It contains 4 tables: `dictionary` and `term`, and `domain` and `dictionary_domain`, which say what each dictionary is about.

### `dictionary` table

| Column | Type | Description |
|:---|:---|:---|
| `id` | INTEGER | Primary key |
| `name_arabic` | VARCHAR | Dictionary name in Arabic |
| `name_english` | VARCHAR | Dictionary name in English |
| `name_french` | VARCHAR | Dictionary name in French |
| `nbr_entries` | INTEGER | Number of terms in the dictionary |
| `name_tech` | VARCHAR | Technical/slug name (unique) |
| `wikidata_id` | VARCHAR | Wikidata item ID for the dictionary |
| `archive_org_url` | VARCHAR | Scan of the paper dictionary on archive.org (`https://archive.org/details/<item>`), as in Wikidata's P953 |
| `page_offset` | INTEGER | Printed page `p` is page `p + page_offset` of the scan (Wikidata's P8330). Its archive.org link is `<archive_org_url>/page/n<p + page_offset - 1>/mode/1up` |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record last update timestamp |

### `term` table

| Column | Type | Description |
|:---|:---|:---|
| `id` | INTEGER | Primary key |
| `arabic` | VARCHAR | Term in Arabic |
| `english` | VARCHAR | Term in English |
| `french` | VARCHAR | Term in French |
| `description` | VARCHAR | Term description (usually in Arabic) |
| `dictionary_id` | INTEGER | Foreign key to `dictionary.id` |
| `page` | INTEGER | Printed page number in the source document (if applicable) |
| `uri` | VARCHAR | Source URI/link |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record last update timestamp |

### `domain` table

A domain is a subject that dictionaries are about (mathematics, medicine, law…). The domains are the values of "main subject" ([P921](https://www.wikidata.org/wiki/Property:P921)) on the dictionaries' Wikidata items, under shorter names: `رياضيات` / `Mathematics` for the item "mathematical terminology".

| Column | Type | Description |
|:---|:---|:---|
| `id` | INTEGER | Primary key |
| `name_tech` | VARCHAR | Technical/slug name (unique), e.g. `mathematics` |
| `name_arabic` | VARCHAR | Domain name in Arabic |
| `name_english` | VARCHAR | Domain name in English |
| `name_french` | VARCHAR | Domain name in French |
| `wikidata_id` | VARCHAR | The Wikidata item used as the P921 value, e.g. `Q66785817` |

### `dictionary_domain` table

One row per domain of a dictionary: every dictionary has at least one, and a dictionary on two subjects has two.

| Column | Type | Description |
|:---|:---|:---|
| `dictionary_id` | INTEGER | Foreign key to `dictionary.id` |
| `domain_id` | INTEGER | Foreign key to `domain.id` |

The terms of one domain:

```sql
SELECT t.*
FROM term t
JOIN dictionary_domain dd ON dd.dictionary_id = t.dictionary_id
JOIN domain dm ON dm.id = dd.domain_id
WHERE dm.name_tech = 'mathematics';
```


## Hugging Face dataset

The same data is published as Parquet on the Hugging Face Hub at [forzagreen/arabterm](https://huggingface.co/datasets/forzagreen/arabterm), regenerated automatically on every change to the database. The default config is the `term` table with the dictionary's `name_tech` joined in as `dictionary`; the `dictionaries` config is the `dictionary` table.

```python
from datasets import load_dataset

terms = load_dataset("forzagreen/arabterm")
dictionaries = load_dataset("forzagreen/arabterm", "dictionaries")
domains = load_dataset("forzagreen/arabterm", "domains")
```

Or straight from Parquet, with pandas, polars or DuckDB:

```python
import pandas as pd

terms = pd.read_parquet("hf://datasets/forzagreen/arabterm/data/terms.parquet")
```

The dataset card describes the columns and lists the dictionaries and their domains.


## Dictionaries

<!-- DICTIONARIES_TABLE_START — auto-generated by `make readme`; do not edit by hand -->
| العربية | English / Français | Domain | Entries | Wikidata |
|:---|:---|:---|---:|:---:|
| مسرد مصطلحات الرقابة النووية (هيئة الرقابة، 2026) | Nuclear Regulatory Glossary (2026)<br />Glossaire de la réglementation nucléaire (2026) | Engineering | 518 | [Q142264077](https://www.wikidata.org/wiki/Q142264077) |
| مسرد مصطلحات الأمان الصادر عن الوكالة الدولية للطاقة الذرية (2007) | IAEA Nuclear Safety and Security Glossary (2007)<br />Glossaire de sûreté et de sécurité nucléaires de l’AIEA (2007) | Engineering | 916 | [Q142264264](https://www.wikidata.org/wiki/Q142264264) |
| المعجم الموحد لمصطلحات الهندسة الميكانيكية (1999) | The Unified Dictionary of Mechanical Engineering Terms (1999)<br />Dictionnaire unifié des termes de génie mécanique (1999) | Engineering | 2828 | [Q116002148](https://www.wikidata.org/wiki/Q116002148) |
| معجم المصطلحات السينمائية (2026) | Cinematic Terminology Glossary (2026)<br />Glossaire de la terminologie cinématographique (2026) | Arts | 2814 | [Q141609371](https://www.wikidata.org/wiki/Q141609371) |
| معجم المصطلحات السياحية (2013) | Lexicon of Touristic Terms (2013)<br />Lexique des termes touristiques (2013) | Anthropology | 3020 | [Q121359340](https://www.wikidata.org/wiki/Q121359340) |
| المعجم الموحد لمصطلحات محو الأمية وتعليم الكبار (2016) | Unified Dictionary of Literacy and Adult Education Terms (2016)<br />Dictionnaire unifié des termes de l'alphabétisation et de l'éducation des adultes (2016) | Education | 481 | [Q116282880](https://www.wikidata.org/wiki/Q116282880) |
| المعجم الموسوعي لمصطلحات الكمبيوتر (1996) | Encyclopedic Dictionary of Computer Terminology (1996)<br />Dictionnaire encyclopédique des termes informatiques (1996) | Computing | 3032 | [Q123703339](https://www.wikidata.org/wiki/Q123703339) |
| معجم وحدات القياس العالمية (1988) | Dictionary of International Units of Measurement (1988)<br />Dictionnaire des unités de mesure internationales (1988) | Science | 914 | [Q141487035](https://www.wikidata.org/wiki/Q141487035) |
| المعجم العربي لمصطلحات الانتخابات (2014) | Arabic Lexicon of Electoral Terminology (2014)<br />Lexique arabe de terminologie électorale (2014) | Politics | 481 | [Q125350759](https://www.wikidata.org/wiki/Q125350759) |
| معجم ألفاظ الحضارة (ج.1، مجمع دمشق، 2014) | Dictionary of Civilisation Vocabulary (Vol. 1, Arab Academy of Damascus, 2014)<br />Dictionnaire du vocabulaire de la civilisation (vol. 1, Académie de langue arabe de Damas, 2014) | Anthropology | 869 | [Q112667705](https://www.wikidata.org/wiki/Q112667705) |
| المعجم الفلكي (1935) | An Astronomical Glossary (1935)<br />Un glossaire astronomique (1935) | Physics | 903 | [Q125167999](https://www.wikidata.org/wiki/Q125167999) |
| مسرد مصطلحات الضمانات الصادر عن الوكالة الدولية للطاقة الذرية (2023) | IAEA Safeguards Glossary (2023)<br />Glossaire des garanties de l’AIEA (2023) | Physics | 443 | [Q130889236](https://www.wikidata.org/wiki/Q130889236) |
| المعجم الموحد لمصطلحات كرة القدم (2023) | The Unified Dictionary of Football Terms (2023)<br />Dictionnaire terminologique unifié du football (2023) | Sports | 909 | [Q116455358](https://www.wikidata.org/wiki/Q116455358) |
| قاموس الرياضيات (دار النعمان، 2017) | Math Dictionary (Dar-El-Noamane, 2017)<br />Dictionnaire de mathématiques (Dar-El-Noamane, 2017) | Mathematics | 1938 | [Q130325501](https://www.wikidata.org/wiki/Q130325501) |
| فهرس دليل اليونسكو في مصطلحات تكنولوجيا المعلومات (اليونسكو، 2022) | UNESCO Guide to Information Technology Terms (UNESCO, 2022)<br />Guide de l'UNESCO des termes des technologies de l'information (UNESCO, 2022) | Computing | 337 | [Q139754870](https://www.wikidata.org/wiki/Q139754870) |
| موسوعة الشاشة الكبيرة (لبنان ناشرون، 2012) | Encyclopedia of the Big Screen (Librairie du Liban, 2012)<br />Encyclopédie du grand écran (Librairie du Liban, 2012) | Arts | 8864 | [Q141610118](https://www.wikidata.org/wiki/Q141610118) |
| معجم المصطلحات العلمية والفنية والهندسية الجديد (لبنان ناشرون، 2018) | A New Dictionary of Scientific and Technical Terms (Librairie du Liban, 2018)<br />Un nouveau dictionnaire de termes scientifiques et techniques (Librairie du Liban, 2018) | Science | 71561 | [Q12244028](https://www.wikidata.org/wiki/Q12244028) |
| المعجم العسكري (لبنان ناشرون، 2011) | Military Dictionary (Librairie du Liban, 2011)<br />Dictionnaire militaire (Librairie du Liban, 2011) | Military | 22883 | [Q138767450](https://www.wikidata.org/wiki/Q138767450) |
| معجم المصطلحات البينية: مجال اللسانيات (المجمع الجزائري، 2026) | Dictionary of Interdisciplinary Terms: Linguistics (AALA, 2026)<br />Dictionnaire des termes interdisciplinaires : domaine de la linguistique (AALA, 2026) | Linguistics | 102 | [Q141645945](https://www.wikidata.org/wiki/Q141645945) |
| قاموس المصطلحات المالية الأكثر استخدامًا بالأسواق المالية (2019) | Dictionary of the Most Used Financial Terms in Financial Markets (UASA, 2019)<br />Dictionnaire des termes financiers les plus utilisés sur les marchés financiers (UASA, 2019) | Economics | 1046 | [Q138342266](https://www.wikidata.org/wiki/Q138342266) |
| المعجم الموحد لمصطلحات اللسانيات (2002) | Linguistics<br />Linguistique | Linguistics | 1729 | [Q114600110](https://www.wikidata.org/wiki/Q114600110) |
| معجم المصطلحات المالية والاقتصادية (مجمع الملك سلمان) | Dictionary of Financial and Economic Terms (KSAA) | Economics | 1892 | [Q141442356](https://www.wikidata.org/wiki/Q141442356) |
| معجم اللغويات الاجتماعية (مجمع الملك سلمان، 2019) | Dictionary of Sociolinguistics (KSAA, 2019) | Sociology, Linguistics | 1179 | [Q141442357](https://www.wikidata.org/wiki/Q141442357) |
| معجم المصطلحات الرياضية (مجمع الملك سلمان، 2025) | Dictionary of Sports Terms (KSAA, 2025) | Sports | 970 | [Q141442360](https://www.wikidata.org/wiki/Q141442360) |
| معجم مصطلحات الإعلام (مجمع الملك سلمان، 2024) | Dictionary of Media Terms (KSAA, 2024) | Sociology | 827 | [Q141442405](https://www.wikidata.org/wiki/Q141442405) |
| معجم المصطلحات الإنمائية (مجمع الملك سلمان) | Dictionary of Development Terms (KSAA) | Economics, Sociology | 791 | [Q141442406](https://www.wikidata.org/wiki/Q141442406) |
| معجم مصطلحات الخطوط الحديدية (مجمع الملك سلمان، 2026) | Dictionary of Railway Terms (KSAA, 2026) | Engineering | 854 | [Q141881807](https://www.wikidata.org/wiki/Q141881807) |
| معجم المصطلحات الموسيقية (مجمع الملك سلمان، 2024) | Dictionary of Musical Terms (KSAA, 2024) | Arts | 579 | [Q141442249](https://www.wikidata.org/wiki/Q141442249) |
| معجم مصطلحات الرياضات الإلكترونية (مجمع الملك سلمان) | Dictionary of Esports Terms (KSAA) | Anthropology | 503 | [Q141442251](https://www.wikidata.org/wiki/Q141442251) |
| معجم اللغة المسرحية (2017) | Dictionary of Theatre Language<br />Dictionnaire de la langue théâtrale | Arts | 741 | [Q123984738](https://www.wikidata.org/wiki/Q123984738) |
| معجم مصطلحات علوم هندسة الطيران والفضاء (2024) | Dictionary of Aerospace Engineering Terms | Engineering | 14621 | [Q141442353](https://www.wikidata.org/wiki/Q141442353) |
| معجم مصطلحات الطاقة (وزارة الطاقة، 2024) | Energy Terminology Dictionary (Ministry of Energy, 2024) | Engineering | 1569 | [Q141133750](https://www.wikidata.org/wiki/Q141133750) |
| معجم المصطلحات الإحصائية (الهيئة العامة للإحصاء) | Glossary of Statistical Terms | Economics, Mathematics | 1389 | [Q133330920](https://www.wikidata.org/wiki/Q133330920) |
| معجم مصطلحات تصنيع السيارات الكهربائية وصيانتها (الأكاديمية الوطنية للسيارات والمركبات) | Dictionary of Electric Vehicle Manufacturing and Maintenance Terms | Engineering | 1061 | [Q141442359](https://www.wikidata.org/wiki/Q141442359) |
| مسرد المصطلحات القانونية (شعبة الترجمة الرسمية بهيئة الخبراء) | Glossary of Legal Terms (Official Translation Division, Board of Experts) | Law | 755 | [Q141442407](https://www.wikidata.org/wiki/Q141442407) |
| قاموس العقود والمشتريات وسلاسل الإمداد (2022) | Dictionary of Contracts, Procurement and Supply Chains | Economics, Law | 2249 | [Q125692651](https://www.wikidata.org/wiki/Q125692651) |
| معجم الاقتصاد المعاصر (2009) | Dictionary of Modern Economics | Economics | 6107 | [Q141443387](https://www.wikidata.org/wiki/Q141443387) |
| معجم مصطلحات العلم والتكنولوجيا (ج.1) | Dictionary of Science and Technology Terms (Vol. 1) | Science | 24028 | [Q130298866](https://www.wikidata.org/wiki/Q130298866) |
| معجم مصطلحات الإعلام (مجمع دمشق، 2022) | Dictionary of Media Terms (Damascus Academy)<br />Dictionnaire des termes des médias | Sociology, Information | 2525 | [Q135471933](https://www.wikidata.org/wiki/Q135471933) |
| دليل المصطلحات الحاسوبية العربية (المجمع الأردني، 2026) | Guide to Arabic Computing Terminology (Jordan Academy of Arabic, 2026) | Computing | 688 | [Q139719120](https://www.wikidata.org/wiki/Q139719120) |
| معجم مصطلحات الكيمياء (مجمع دمشق، 2014) | Dictionary of Chemistry Terms (Damascus Academy)<br />Dictionnaire des termes de chimie | Chemistry | 5609 | [Q113378673](https://www.wikidata.org/wiki/Q113378673) |
| معجم مصطلحات الفيزياء (مجمع دمشق، 2015) | Dictionary of Physics Terms (Damascus Academy)<br />Dictionnaire des termes de physique | Physics | 5928 | [Q113016239](https://www.wikidata.org/wiki/Q113016239) |
| معجم مصطلحات الرياضيات (مجمع دمشق، 2018) | Dictionary of Mathematics Terms (Damascus Academy)<br />Dictionnaire des termes de mathématiques | Mathematics | 7059 | [Q108593221](https://www.wikidata.org/wiki/Q108593221) |
| المعجم العربي للملكية الفكرية (2021) | Arabic Glossary of Intellectual Property | Law | 276 | [Q133934820](https://www.wikidata.org/wiki/Q133934820) |
| معجم مصطلحات سكك الحديد (2017) | Glossary of Railway Terms | Engineering | 345 | [Q131987385](https://www.wikidata.org/wiki/Q131987385) |
| قاموس مصطلحات الطوارئ والكوارث (2011) | Dictionary of Disaster and Emergency Terminology | Military | 1220 | [Q108224091](https://www.wikidata.org/wiki/Q108224091) |
| معجم مصطلحات كوفيد-19 (2020) | Dictionary of COVID-19 Terms<br />Dictionnaire terminologique du COVID-19 | Medicine | 188 | [Q112724717](https://www.wikidata.org/wiki/Q112724717) |
| مسرد مصطلحات أمن المعلومات: إنجليزي - عربي | Glossary of Information Security Terms: English - Arabic | Computing | 400 | [Q124816352](https://www.wikidata.org/wiki/Q124816352) |
| قاموس المؤسسة للمصطلحات والعبارات والمسميات المتداولة في القطاع النفطي (2007) | KPC Dictionary of Terms, Expressions and Names Used in the Oil Sector | Engineering | 487 | [Q132396287](https://www.wikidata.org/wiki/Q132396287) |
| المعجم الموحد لمصطلحات التربية على الإبداع والابتكار (2020) | The unified dictionary of educational terms on creativity and innovation<br />Dictionnaire terminologique unifié de l'éducation à la créativité et à l'innovation | Education | 428 | [Q116443862](https://www.wikidata.org/wiki/Q116443862) |
| المعجم الموحد لمصطلحات المناهج وطرائق التدريس (2020) | The unified dictionary of curricula and teaching methods terms<br />Dictionnaire terminologique unifié des programmes scolaires et des méthodes d'enseignement | Education | 383 | [Q116390963](https://www.wikidata.org/wiki/Q116390963) |
| عرب آيز | Arabeyes | Computing | 3885 | [Q142195103](https://www.wikidata.org/wiki/Q142195103) |
| المعجم الموحد لمصطلحات التعدين (2026) | The unified dictionary of mining terms | Engineering | 1853 | [Q138820643](https://www.wikidata.org/wiki/Q138820643) |
| معجم البيانات والذكاء الاصطناعي (الإصدار الثالث، 2026) | Data and AI Glossary | Computing | 1423 | [Q141499878](https://www.wikidata.org/wiki/Q141499878) |
| المَكنَز الزراعي متعدد اللغات | AGROVOC | Engineering, Biology | 22212 | [Q292649](https://www.wikidata.org/wiki/Q292649) |
| معجم المصطلحات الطبية (ج.3، 1997) |  | Medicine | 3098 | [Q124465892](https://www.wikidata.org/wiki/Q124465892) |
| معجم المصطلحات الطبية (ج.2، 2003) |  | Medicine | 4383 | [Q124465865](https://www.wikidata.org/wiki/Q124465865) |
| معجم المصطلحات الطبية (ج.1، 1985) |  | Medicine | 3915 | [Q124465852](https://www.wikidata.org/wiki/Q124465852) |
| المعجم الموحد لمصطلحات الحكامة التربوية (2020) | The unified dictionary of educational governance terms<br />Dictionnaire terminologique unifié de la gouvernance éducative | Education | 490 | [Q116431458](https://www.wikidata.org/wiki/Q116431458) |
| المعجم الموحد لمصطلحات الاستراتيجيات التربوية والتعليمية (2020) | The Unifed Dictionary Of Educational Strategies Terms<br />Dictionnaire terminologique unifié des stratégies de l'éducation et de l'enseignement | Education | 592 | [Q116392774](https://www.wikidata.org/wiki/Q116392774) |
| المعجم الموحد لمصطلحات الإشراف التربوي (2020) | The unified dictionary of educational supervision terms<br />Dictionnaire terminologique unifié de la supervision pédagogique | Education | 340 | [Q116437316](https://www.wikidata.org/wiki/Q116437316) |
| المورد الحديث (2008) | Al-Mawrid Al-Hadeeth | English language | 62265 | [Q112315598](https://www.wikidata.org/wiki/Q112315598) |
| المعجم الطبي الموحد (2009) | The Unified Medical Dictionary<br />Le dictionnaire médical unifié | Medicine | 132975 | [Q113466993](https://www.wikidata.org/wiki/Q113466993) |
| معجم مصطلحات المعلوماتية (2000) | Dictionary of Information Technology Terms | Computing | 7031 | [Q108408025](https://www.wikidata.org/wiki/Q108408025) |
| موسوعة الكهرباء (IEC 60050) | Electropedia | Engineering | 20611 | [Q1667710](https://www.wikidata.org/wiki/Q1667710) |
| مسرد الجغرافيا والتاريخ (الألكسو) | Geography and History (ALECSO)<br />Géographie et Histoire (ALECSO) | Sociology, Geology | 5724 | [Q141044804](https://www.wikidata.org/wiki/Q141044804) |
| مسرد اللغة والأدب (الألكسو) | Language and Literature (ALECSO)<br />Langue et Littérature (ALECSO) | Literature | 1494 | [Q141505412](https://www.wikidata.org/wiki/Q141505412) |
| مسرد الفن، التسلية والرياضة (الألكسو) | Arts, Recreation and Sports (ALECSO)<br />Art, Divertissement et sports (ALECSO) | Arts | 5269 | [Q141104930](https://www.wikidata.org/wiki/Q141104930) |
| مسرد الفلسفة وعلم النفس (الألكسو) | Philosophy and Psychology (ALECSO)<br />Philosophie et Psychologie (ALECSO) | Philosophy | 1350 | [Q141104937](https://www.wikidata.org/wiki/Q141104937) |
| مسرد الإعلام والتواصل (الألكسو) | Information and Communication (ALECSO)<br />Information et Communication (ALECSO) | Information | 6081 | [Q141104936](https://www.wikidata.org/wiki/Q141104936) |
| المعجم الموحد لمصطلحات تقانات الأغذية (2004) | Nutrition Technologies<br />Technologies Alimentaires | Engineering | 2686 | [Q116186863](https://www.wikidata.org/wiki/Q116186863) |
| المعجم الموحد للمصطلحات المهنية والتقنية ج. 1: طباعة - كهرباء (1996) | Printing - Electricity<br />Imprimerie - Electricité | Engineering | 2838 | [Q115776451](https://www.wikidata.org/wiki/Q115776451) |
| المعجم الموحد للمصطلحات المهنية والتقنية ج. 2: بناء - تجارة (1999) | Masonry - Carpentry<br />Maçonnerie - Charpenterie | Engineering, Economics | 3731 | [Q115776448](https://www.wikidata.org/wiki/Q115776448) |
| المعجم الموحد لمصطلحات علم التشريح العياني (2015) | Gross Anatomy<br />Anatomie Macroscopique | Medicine | 5779 | [Q116262180](https://www.wikidata.org/wiki/Q116262180) |
| المعجم الموحد لمصطلحات الطب البيطري (2010) | Veterinary Medicine<br />Médecine Vétérinaire | Medicine, Biology | 2741 | [Q116213330](https://www.wikidata.org/wiki/Q116213330) |
| المعجم الموحد لمصطلحات الاستشعار عن بعد (2000) | Remote Sensing<br />Télédétection | Engineering, Military | 1196 | [Q116167591](https://www.wikidata.org/wiki/Q116167591) |
| المعجم الموحد لمصطلحات الحرب الإلكترونية (2004) | Electronic Warfare<br />Guerre éléctronique | Engineering, Military | 1021 | [Q116186852](https://www.wikidata.org/wiki/Q116186852) |
| المعجم الموحد لمصطلحات علم الصيدلة (2009) | Pharmacy<br />Pharmacie | Medicine, Chemistry | 3686 | [Q116203617](https://www.wikidata.org/wiki/Q116203617) |
| المعجم الموحد لمصطلحات علم الوراثة (2009) | Genetics<br />Génétique | Medicine, Biology | 2542 | [Q116195788](https://www.wikidata.org/wiki/Q116195788) |
| المعجم الموحد لمصطلحات علم الصحة وجسم الانسان (1992) | Hygienics and Human Body<br />Santé et Corps Humain | Medicine | 2134 | [Q113574525](https://www.wikidata.org/wiki/Q113574525) |
| المعجم الموحد لمصطلحات علم الأحياء (1993) | Biology<br />Biologie | Biology | 6561 | [Q114972534](https://www.wikidata.org/wiki/Q114972534) |
| المعجم الموحد لمصطلحات النفط (1999) | Petroleum<br />Pétrole | Engineering | 6089 | [Q115957618](https://www.wikidata.org/wiki/Q115957618) |
| المعجم الموحد لمصطلحات علوم البحار (2000) | Oceanology<br />Océanographie | Biology | 3913 | [Q116174633](https://www.wikidata.org/wiki/Q116174633) |
| المعجم الموحد لمصطلحات الأرصاد الجوية (1999) | Meteorology<br />Météorologie | Geology | 2031 | [Q116153637](https://www.wikidata.org/wiki/Q116153637) |
| مسرد علوم الزلازل (الألكسو) | Seismology (ALECSO)<br />Séismologie (ALECSO) | Geology | 4722 | [Q141105349](https://www.wikidata.org/wiki/Q141105349) |
| المعجم الموحد لمصطلحات الجيولوجيا (2000) | Geology<br />Géologie | Geology | 4623 | [Q115944157](https://www.wikidata.org/wiki/Q115944157) |
| المعجم الموحد لمصطلحات الكيمياء (1992) | Chemistry<br />Chimie | Chemistry | 4532 | [Q114804479](https://www.wikidata.org/wiki/Q114804479) |
| المعجم الموحد لمصطلحات الفيزياء العامة والنووية (1989) | Physics<br />Physique | Physics | 6315 | [Q113987323](https://www.wikidata.org/wiki/Q113987323) |
| المعجم الموحد لمصطلحات الرياضيات والفلك (1990) | Mathematics and Astronomy<br />Mathématiques et Astronomie | Mathematics, Astronomy | 4068 | [Q114600477](https://www.wikidata.org/wiki/Q114600477) |
| المعجم الموحد لمصطلحات القانون (2017) | Law<br />Droit | Law | 3218 | [Q115934214](https://www.wikidata.org/wiki/Q115934214) |
| المعجم الموحد لمصطلحات التجارة والمحاسبة (1995) | Commerce and Accounting<br />Commerce et Comptabilité | Economics | 8862 | [Q115770013](https://www.wikidata.org/wiki/Q115770013) |
| المعجم الموحد لمصطلحات الاقتصاد (2000) | Economics<br />Economie | Economics | 2036 | [Q115944244](https://www.wikidata.org/wiki/Q115944244) |
| مسرد علم الاجتماع والأنثروبولوجيا (الألكسو) | Sociology and Anthropology (ALECSO)<br />Sociologie et Anthropologie (ALECSO) | Sociology | 1261 | [Q141104938](https://www.wikidata.org/wiki/Q141104938) |
| مسرد التربية (الألكسو) | Education (ALECSO) | Education | 2988 | [Q141104933](https://www.wikidata.org/wiki/Q141104933) |
| المعجم الموحد لمصطلحات التقنيات التربوية (1999) | Educational and Computer Techniques<br />Techniques Pédagogiques et Informatiques | Education | 1524 | [Q116036314](https://www.wikidata.org/wiki/Q116036314) |
| مسرد المناخ والبيئة وإدارة النفايات الصلبة (الألكسو) | Climate, Environment and Solid Waste management (ALECSO)<br />Climat, l’Environment, et la Gestion des déchets solides (ALECSO) | Geology | 7040 | [Q141104932](https://www.wikidata.org/wiki/Q141104932) |
| المعجم الموحد لمصطلحات تقانة (تكنولوجيا) المعلومات (2011) | Information and Communication<br />Technologie de l’Information | Computing | 1369 | [Q111267300](https://www.wikidata.org/wiki/Q111267300) |
| المعجم الموحد لمصطلحات الهندسة المدنية (2012) | Civil Engineering<br />Génie Civil | Engineering | 3943 | [Q116255030](https://www.wikidata.org/wiki/Q116255030) |
| مسرد صناعة النسيج (الألكسو) | Textiles Industries (ALECSO)<br />l’Industrie Textile (ALECSO) | Engineering | 4513 | [Q141104939](https://www.wikidata.org/wiki/Q141104939) |
| مسرد النقل والبنية التحتية (الألكسو) | Transport and Infrastructure (ALECSO)<br />Transport et Infrastructure (ALECSO) | Engineering | 5558 | [Q141215921](https://www.wikidata.org/wiki/Q141215921) |
| مسرد الهندسة الكهربائية (الألكسو) | Electrical Engineering (ALECSO)<br />Génie Electrique (ALECSO) | Engineering | 2569 | [Q141104934](https://www.wikidata.org/wiki/Q141104934) |
| مسرد الطاقات المتجددة (الألكسو) | Renewable Energy (ALECSO)<br />Energies Renouvelables (ALECSO) | Engineering | 7289 | [Q141105348](https://www.wikidata.org/wiki/Q141105348) |
| مسرد هندسة المياه (الألكسو) | Water Engineering (ALECSO)<br />Technologie de l’eau (ALECSO) | Engineering, Geology | 8644 | [Q141137252](https://www.wikidata.org/wiki/Q141137252) |
| مسرد هندسة وتكنولوجيا السيارات (الألكسو) | Automotive Engineering (ALECSO)<br />Technique automobile (ALECSO) | Engineering | 4605 | [Q141104931](https://www.wikidata.org/wiki/Q141104931) |
<!-- DICTIONARIES_TABLE_END -->


## Website

A static reference site is published at [forzagreen.github.io/arabterm](https://forzagreen.github.io/arabterm/), with one page per dictionary. Live search is delegated to [Wikitermbase](https://wikitermbase.toolforge.org/); the site itself is purely a static index plus paginated term tables and per-dictionary JSON downloads.

The site is built with [Astro](https://astro.build/) and reads `arabterm.db` directly at build time, so it stays in sync with the data on every push. See [website/README.md](website/README.md) for the build setup.

## Generating database dumps

This is an internal development workflow for generating the SQL dumps in [db/](db/) for SQLite and MariaDB. This requires Docker and [uv](https://docs.astral.sh/uv/). Copy `example.env` to `.env` and set `MARIADB_PASSWORD` — the Make targets pass `.env` to `uv run` so no manual sourcing is needed.

Run the full pipeline (start MariaDB, migrate from SQLite, verify search, and write the SQL dumps for both engines):

```sh
make regenerate_dumps
```

The pipeline is safe to run on a small machine: terms are copied to MariaDB in batches, and the MariaDB container is capped at half of the CPUs and a quarter of the memory available to Docker. Override the caps with `make regenerate_dumps MARIADB_CPUS=4 MARIADB_MEMORY=4g`.

When a PR touching `db/mariadb/arabterm.sql.gz` is merged to `main`, [`.github/workflows/notify-wikitermbase.yml`](.github/workflows/notify-wikitermbase.yml) dispatches an event to [forzagreen/wikitermbase](https://github.com/forzagreen/wikitermbase), which auto-opens a PR there with the regenerated `db/arabterm.sql`. That PR is titled after the arabterm commit and its description carries the commit message and a summary of the data changes (dictionaries and terms added, removed or modified). Merging that PR triggers the automated `mariadb` import on Toolforge.

When `arabterm.db.gz` changes on `main`, [`.github/workflows/publish-huggingface.yml`](.github/workflows/publish-huggingface.yml) also re-exports the database as Parquet and pushes it, with its dataset card, to [forzagreen/arabterm](https://huggingface.co/datasets/forzagreen/arabterm) on Hugging Face. The same export runs locally with `make hf_export` (into the gitignored `hf/` folder) and `make hf_push` (needs `HF_TOKEN` in `.env`); both need the `hf` extra, which `make init` installs.

## History

This project started in 2022 as a web scraping effort to extract dictionaries from [arabterm.org](https://www.arabterm.org/), a set of multilingual technical dictionaries organized by technical domains and industry sectors. The extraction was performed using Python, [Selenium](https://selenium-python.readthedocs.io/), and [lxml](https://lxml.de/lxmlhtml.html).

Over time, the project evolved to include additional Arabic/English/French dictionaries from various sources, becoming a broader multilingual terminology dataset.


## Citation

If you use this data, please cite the repository (GitHub's "Cite this repository" button uses [CITATION.cff](CITATION.cff)) and credit the dictionary the terms come from, which the `dictionary` table identifies:

```bibtex
@misc{arabterm,
  author    = {Tellat, Wael},
  title     = {arabterm: Arabic/English/French terminology dictionaries},
  year      = {2022},
  publisher = {GitHub},
  url       = {https://github.com/forzagreen/arabterm},
  note      = {Dataset: \url{https://huggingface.co/datasets/forzagreen/arabterm}}
}
```


## References

- [https://wikitermbase.toolforge.org/](https://wikitermbase.toolforge.org/)
- [https://forzagreen.github.io/arabterm/](https://forzagreen.github.io/arabterm/)
- [ويكيبيديا:مصادر موثوقة/معاجم وقواميس وأطالس](https://ar.wikipedia.org/wiki/%D9%88%D9%8A%D9%83%D9%8A%D8%A8%D9%8A%D8%AF%D9%8A%D8%A7:%D9%85%D8%B5%D8%A7%D8%AF%D8%B1_%D9%85%D9%88%D8%AB%D9%88%D9%82%D8%A9/%D9%85%D8%B9%D8%A7%D8%AC%D9%85_%D9%88%D9%82%D9%88%D8%A7%D9%85%D9%8A%D8%B3_%D9%88%D8%A3%D8%B7%D8%A7%D9%84%D8%B3)
 
