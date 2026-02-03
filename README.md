# arabterm

This repository is a collection of Arabic/English/French multilingual dictionaries. It serves as the primary data source for [Wiki Term Base](https://wikitermbase.toolforge.org/), a tool designed to standardize terminology used on Arabic Wikipedia and accelerate vocabulary translation.

The dictionaries are available as an [SQLite](https://www.sqlite.org/) database ([arabterm.db](arabterm.db)), and as SQL dumps for SQLite and MariaDB in the [db/](db/) folder.


  - [SQLite database](#sqlite-database)
  - [Dictionaries](#dictionaries)
  - [Other datasets](#other-datasets)
  - [References](#references)


## SQLite database

The full extract is in the SQLite database file [arabterm.db](arabterm.db).

It contains 2 tables: `dictionary` and `term`.

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
| `page` | INTEGER | Page number in source document (if applicable) |
| `uri` | VARCHAR | Source URI/link |
| `created_at` | DATETIME | Record creation timestamp |
| `updated_at` | DATETIME | Record last update timestamp |


## Dictionaries

| العربية | English / Français | Entries | Wikidata |
|:---|:---|---:|:---:|
| المورد الحديث (2008) | Al-Mawrid Al-Hadeeth | 62266 | [Q112315598](https://www.wikidata.org/wiki/Q112315598) |
| المَكنَز الزراعي متعدد اللغات | AGROVOC | 22212 | [Q292649](https://www.wikidata.org/wiki/Q292649) |
| مسرد الفن، التسلية والرياضة، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Arts, Recreation and Sports<br />Art, Divertissement et sports | 5269 | |
| مسرد هندسة وتكنولوجيا السيارات، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Automotive Engineering<br />Technique automobile | 4605 | |
| المعجم الموحد لمصطلحات علم الأحياء (1993) | Biology<br />Biologie | 6561 | [Q114972534](https://www.wikidata.org/wiki/Q114972534) |
| المعجم الموحد لمصطلحات الكيمياء (1992) | Chemistry<br />Chimie | 4532 | [Q114804479](https://www.wikidata.org/wiki/Q114804479) |
| المعجم الموحد لمصطلحات الهندسة المدنية (2012) | Civil Engineering<br />Génie Civil | 3943 | [Q116255030](https://www.wikidata.org/wiki/Q116255030) |
| مسرد المناخ والبيئة وإدارة النفايات الصلبة، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Climate, Environment and Solid Waste management<br />Climat, l'Environment, et la Gestion des déchets solides | 7040 | |
| المعجم الموحد لمصطلحات التجارة والمحاسبة (1995) | Commerce and Accounting<br />Commerce et Comptabilité | 8862 | [Q115770013](https://www.wikidata.org/wiki/Q115770013) |
| معجم البيانات والذكاء الاصطناعي (2024) | Data and AI Glossary | 1241 | [Q111421033](https://www.wikidata.org/wiki/Q111421033) |
| معجم مصطلحات المعلوماتية (2000) | Dictionary of Information Technology Terms | 7031 | [Q108408025](https://www.wikidata.org/wiki/Q108408025) |
| المعجم الموحد لمصطلحات الاقتصاد (2000) | Economics<br />Economie | 2036 | [Q115944244](https://www.wikidata.org/wiki/Q115944244) |
| مسرد التربية، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Education | 2988 | |
| المعجم الموحد لمصطلحات التقنيات التربوية (1999) | Educational and Computer Techniques<br />Techniques Pédagogiques et Informatiques | 1524 | [Q116036314](https://www.wikidata.org/wiki/Q116036314) |
| مسرد الهندسة الكهربائية، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Electrical Engineering<br />Génie Electrique | 2569 | |
| المعجم الموحد لمصطلحات الحرب الإلكترونية (2004) | Electronic Warfare<br />Guerre éléctronique | 1021 | [Q116186852](https://www.wikidata.org/wiki/Q116186852) |
| موسوعة الكهرباء (IEC 60050) | Electropedia | 20611 | [Q1667710](https://www.wikidata.org/wiki/Q1667710) |
| المعجم الموحد لمصطلحات علم الوراثة (2009) | Genetics<br />Génétique | 2542 | [Q116195788](https://www.wikidata.org/wiki/Q116195788) |
| مسرد الجغرافيا والتاريخ، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Geography and History<br />Géographie et Histoire | 5724 | |
| المعجم الموحد لمصطلحات الجيولوجيا (2000) | Geology<br />Géologie | 4623 | [Q115944157](https://www.wikidata.org/wiki/Q115944157) |
| المعجم الموحد لمصطلحات علم التشريح العياني (2015) | Gross Anatomy<br />Anatomie Macroscopique | 5779 | [Q116262180](https://www.wikidata.org/wiki/Q116262180) |
| المعجم الموحد لمصطلحات علم الصحة وجسم الانسان (1992) | Hygienics and Human Body<br />Santé et Corps Humain | 2134 | [Q113574525](https://www.wikidata.org/wiki/Q113574525) |
| المعجم الموحد لمصطلحات تقانة (تكنولوجيا) المعلومات (2011) | Information and Communication<br />Technologie de l'Information | 1369 | [Q111267300](https://www.wikidata.org/wiki/Q111267300) |
| مسرد الإعلام والتواصل، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Information and Communication<br />Information et Communication | 6081 | |
| المعجم الموحد لمصطلحات اللسانيات (2002) | Language and Literature<br />Langue et Littérature | 3223 | [Q108756680](https://www.wikidata.org/wiki/Q108756680) |
| المعجم الموحد لمصطلحات القانون (2017) | Law<br />Droit | 3218 | [Q115934214](https://www.wikidata.org/wiki/Q115934214) |
| المعجم الموحد للمصطلحات المهنية والتقنية ج. 2: بناء - تجارة (1999) | Masonry - Carpentry<br />Maçonnerie - Charpenterie | 3731 | [Q115776448](https://www.wikidata.org/wiki/Q115776448) |
| المعجم الموحد لمصطلحات الرياضيات والفلك (1990) | Mathematics and Astronomy<br />Mathématiques et Astronomie | 4068 | [Q114600477](https://www.wikidata.org/wiki/Q114600477) |
| المعجم الموحد لمصطلحات الأرصاد الجوية (1999) | Meteorology<br />Météorologie | 2031 | [Q116153637](https://www.wikidata.org/wiki/Q116153637) |
| المعجم الموحد لمصطلحات تقانات الأغذية (2004) | Nutrition Technologies<br />Technologies Alimentaires | 2686 | [Q116186863](https://www.wikidata.org/wiki/Q116186863) |
| المعجم الموحد لمصطلحات علوم البحار (2000) | Oceanology<br />Océanographie | 3913 | [Q116174633](https://www.wikidata.org/wiki/Q116174633) |
| المعجم الموحد لمصطلحات النفط (1999) | Petroleum<br />Pétrole | 6089 | [Q115957618](https://www.wikidata.org/wiki/Q115957618) |
| المعجم الموحد لمصطلحات علم الصيدلة (2009) | Pharmacy<br />Pharmacie | 3686 | [Q116203617](https://www.wikidata.org/wiki/Q116203617) |
| مسرد الفلسفة وعلم النفس، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Philosophy and Psychology<br />Philosophie et Psychologie | 1350 | |
| المعجم الموحد لمصطلحات الفيزياء العامة والنووية (1989) | Physics<br />Physique | 6315 | [Q113987323](https://www.wikidata.org/wiki/Q113987323) |
| المعجم الموحد للمصطلحات المهنية والتقنية ج. 1: طباعة - كهرباء (1996) | Printing - Electricity<br />Imprimerie - Electricité | 2838 | [Q115776451](https://www.wikidata.org/wiki/Q115776451) |
| المعجم الموحد لمصطلحات الاستشعار عن بعد (2000) | Remote Sensing<br />Télédétection | 1196 | [Q116167591](https://www.wikidata.org/wiki/Q116167591) |
| المعجم الموحد لمصطلحات الطاقة المتجددة (1996) | Renewable Energy<br />Energies Renouvelables | 7289 | [Q115770286](https://www.wikidata.org/wiki/Q115770286) |
| المعجم الموحد لمصطلحات علوم الزلازل (1999) | Seismology<br />Séismologie | 4722 | [Q115933629](https://www.wikidata.org/wiki/Q115933629) |
| مسرد علم الاجتماع والأنثروبولوجيا، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Sociology and Anthropology<br />Sociologie et Anthropologie | 1261 | |
| مسرد صناعة النسيج، المنظمة العربية للتربية والثقافة والعلوم (موقع ArabTerm) | Textiles Industries<br />l'Industrie Textile | 4513 | |
| المعجم الموحد لمصطلحات الاستراتيجيات التربوية والتعليمية (2020) | The Unifed Dictionary Of Educational Strategies Terms<br />Dictionnaire terminologique unifié des stratégies de l'éducation et de l'enseignement | 592 | [Q116392774](https://www.wikidata.org/wiki/Q116392774) |
| المعجم الطبي الموحد (2009) | The Unified Medical Dictionary<br />Le dictionnaire médical unifié | 132975 | [Q113466993](https://www.wikidata.org/wiki/Q113466993) |
| المعجم الموحد لمصطلحات الحكامة التربوية (2020) | The unified dictionary of educational governance terms<br />Dictionnaire terminologique unifié de la gouvernance éducative | 490 | [Q116431458](https://www.wikidata.org/wiki/Q116431458) |
| المعجم الموحد لمصطلحات الإشراف التربوي (2020) | The unified dictionary of educational supervision terms<br />Dictionnaire terminologique unifié de la supervision pédagogique | 340 | [Q116437316](https://www.wikidata.org/wiki/Q116437316) |
| المعجم الموحد لمصطلحات النقل (2010) | Transport and Infrastructure<br />Transport et Infrastructure | 5558 | [Q116214837](https://www.wikidata.org/wiki/Q116214837) |
| المعجم الموحد لمصطلحات الطب البيطري (2010) | Veterinary Medicine<br />Médecine Vétérinaire | 2741 | [Q116213330](https://www.wikidata.org/wiki/Q116213330) |
| المعجم الموحد لمصطلحات المياه (2000) | Water Engineering<br />Technologie de l'eau | 8644 | [Q116167054](https://www.wikidata.org/wiki/Q116167054) |
| معجم المصطلحات الطبية (ج.1، 1985) | | 3915 | [Q124465852](https://www.wikidata.org/wiki/Q124465852) |
| معجم المصطلحات الطبية (ج.2، 2003) | | 4383 | [Q124465865](https://www.wikidata.org/wiki/Q124465865) |
| معجم المصطلحات الطبية (ج.3، 1997) | | 3098 | [Q124465892](https://www.wikidata.org/wiki/Q124465892) |


## History

This project started in 2022 as a web scraping effort to extract dictionaries from [arabterm.org](http://www.arabterm.org/), a set of multilingual technical dictionaries organized by technical domains and industry sectors. The extraction was performed using Python, [Selenium](https://selenium-python.readthedocs.io/), and [lxml](https://lxml.de/lxmlhtml.html).

Over time, the project evolved to include additional Arabic/English/French dictionaries from various sources, becoming a broader multilingual terminology dataset.


## References

- [https://wikitermbase.toolforge.org/](https://wikitermbase.toolforge.org/)
- [https://forzagreen.github.io/arabterm/](https://forzagreen.github.io/arabterm/)
- [ويكيبيديا:مصادر موثوقة/معاجم وقواميس وأطالس](https://ar.wikipedia.org/wiki/%D9%88%D9%8A%D9%83%D9%8A%D8%A8%D9%8A%D8%AF%D9%8A%D8%A7:%D9%85%D8%B5%D8%A7%D8%AF%D8%B1_%D9%85%D9%88%D8%AB%D9%88%D9%82%D8%A9/%D9%85%D8%B9%D8%A7%D8%AC%D9%85_%D9%88%D9%82%D9%88%D8%A7%D9%85%D9%8A%D8%B3_%D9%88%D8%A3%D8%B7%D8%A7%D9%84%D8%B3)
 
