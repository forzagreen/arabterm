# arabterm


[Arab Term](http://www.arabterm.org/) is a set of multilingual technical dictionaries, organised by technical domains and industry sectors.

This repository provides a full extract of [arabterm.org](http://www.arabterm.org/) dictionaries, in a web interface: [https://forzagreen.github.io/arabterm/](https://forzagreen.github.io/arabterm/)

The extracts are also available in CSV and JSON files, and as [SQLite](https://www.sqlite.org/) database.

The data extraction was performed between March and August of 2022, by web scraping [arabterm.org](http://www.arabterm.org/), using python, [Selenium](https://selenium-python.readthedocs.io/), and [lxml](https://lxml.de/lxmlhtml.html).


  - [SQLite database](#sqlite-database)
  - [CSV files](#csv-files)
  - [Dictionaries](#dictionaries)
  - [References](#references)


## SQLite database

The full extract is in the SQLite database file [arabterm.db](arabterm.db).

It contains 2 tables: `category` and `entry`


## CSV files

There is one CSV file per category in [data/](data/) folder.

All CSV files have the following columns:

- `id` *(integer)*: Entry unique id.
- `english` *(string)*: English translation.
- `arabic` *(string)*: Arabic translation.
- `french` *(string)*: French translation.
- `uri` *(URL)*: Link to the entry in [arabterm.org](http://www.arabterm.org/)
- `description` *(string)*: Entry description in arabic (if exists).
- `vt` *(boolean)*: Validated term.
- `uatv` *(boolean)*: Unified Arabic term, validated during the Arabization Congress organized by the [ALECSO](http://www.alecso.org/nsite/ar/).

Some CSV files have these additional columns:

- `german` *(string)*: German translation. Available for some categories.
See `available_languages` fields in [categories.json](categories.json).
- `image_uri_remote` *(URL)*: Link to the image in arabterm.org (if the entry has one).
Available for categories 2, 22, and 34.
- `image_uri_extract` *(URL)*: Link to the image in this repository (if the entry has one).
Available for categories 2, 22, and 34.

## JSON files

There is one JSON file per category in the folder [website/src/assets/](website/src/assets/)

JSON fields:

- `id` *(string)*: Entry unique id.
- `en` *(string)*: English translation.
- `ar` *(string)*: Arabic translation.
- `fr` *(string)*: French translation.
- `ge` *(string)*: German translation. Available for some categories.
- `d` *(string)*: Entry description in arabic (if exists).


## Dictionaries

In the columns _Extracts_, you can click on the available formats.


| Title in English/French/German | العربية | Entries | Extracts | ArabTerm page |
|:---:|:---:|:---:|:---:|:---:|
| Automotive Engineering<br />Technique automobile<br />Kfz-Technik | هندسة وتكنولوجيا السيارات | 4605 | [web](https://forzagreen.github.io/arabterm/automotive_engineering), [csv](data/automotive_engineering.csv), [json](website/src/assets/automotive_engineering.json) | [1](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=1) |
| Water Engineering<br />Technologie de l’eau<br />Wassertechnik | هندسة المياه | 8644 | [web](https://forzagreen.github.io/arabterm/water_engineering), [csv](data/water_engineering.csv), [json](website/src/assets/water_engineering.json) | [2](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=2) |
| Renewable Energy<br />Energies Renouvelables<br />Erneuerbare Energien | الطاقات المتجددة | 7289 | [web](https://forzagreen.github.io/arabterm/renewable_energy), [csv](data/renewable_energy.csv), [json](website/src/assets/renewable_energy.json) | [22](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=22) |
| Electrical Engineering<br />Génie Electrique<br />Elektrotechnik | الهندسة الكهربائية | 2569 | [web](https://forzagreen.github.io/arabterm/electrical_engineering), [csv](data/electrical_engineering.csv), [json](website/src/assets/electrical_engineering.json) | [26](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=26) |
| Transport and Infrastructure<br />Transport et Infrastructure<br />Transport und Infrastruktur | النقل والبنية التحتية | 5558 | [web](https://forzagreen.github.io/arabterm/transport_infrastructure), [csv](data/transport_infrastructure.csv), [json](website/src/assets/transport_infrastructure.json) | [30](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=30) |
| Textiles Industries<br />l’Industrie Textile<br />Textilindustrie | صناعة النسيج | 4513 | [web](https://forzagreen.github.io/arabterm/textiles_industries), [csv](data/textiles_industries.csv), [json](website/src/assets/textiles_industries.json) | [34](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=34) |
| Civil Engineering<br />Génie Civil<br />Bauingenieurwesen | الهندسة المدنية | 3943 | [web](https://forzagreen.github.io/arabterm/civil_engineering), [csv](data/civil_engineering.csv), [json](website/src/assets/civil_engineering.json) | [39](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=39) |
| Information and Communication<br />Technologie de l’Information<br />Informationstechnologie | تقانة المعلومات | 1369 | [web](https://forzagreen.github.io/arabterm/information_tech), [csv](data/information_tech.csv), [json](website/src/assets/information_tech.json), [scan](https://archive.org/details/ALECSO2011AREN) | [47](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=47) |
| Climate, Environment and Solid Waste management<br />Climat, l’Environment, et la Gestion des déchets solides<br />Klima, Umwelt und Abfallwirtschaft | المناخ والبيئة وإدارة النفايات الصلبة | 7040 | [web](https://forzagreen.github.io/arabterm/climate_environment), [csv](data/climate_environment.csv), [json](website/src/assets/climate_environment.json) | [51](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=51) |
| Educational and Computer Techniques<br />Techniques Pédagogiques et Informatiques<br />Pädagogik und Informatiktechniken | التقنيات التربوية والحاسوبية | 1524 | [web](https://forzagreen.github.io/arabterm/educational_techniques), [csv](data/educational_techniques.csv), [json](website/src/assets/educational_techniques.json) | [644](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=644) |
| Education<br />Education<br />Erziehungswissenschaft | التربية | 2988 | [web](https://forzagreen.github.io/arabterm/education), [csv](data/education.csv), [json](website/src/assets/education.json) | [645](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=645) |
| Sociology and Anthropology<br />Sociologie et Anthropologie<br />Soziologie und Anthropologie | علم الاجتماع والأنثروبولوجيا | 1261 | [web](https://forzagreen.github.io/arabterm/sociology_anthropology), [csv](data/sociology_anthropology.csv), [json](website/src/assets/sociology_anthropology.json) | [646](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=646) |
| Economics<br />Economie<br />Wirtschaft | الاقتصاد | 2036 | [web](https://forzagreen.github.io/arabterm/economics), [csv](data/economics.csv), [json](website/src/assets/economics.json) | [647](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=647) |
| Commerce and Accounting<br />Commerce et Comptabilité<br />Handel und Rechnungswesen | التجارة والمحاسبة | 8862 | [web](https://forzagreen.github.io/arabterm/commerce_accounting), [csv](data/commerce_accounting.csv), [json](website/src/assets/commerce_accounting.json) | [648](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=648) |
| Law<br />Droit<br />Rechtswissenschaft | القانون | 3218 | [web](https://forzagreen.github.io/arabterm/law), [csv](data/law.csv), [json](website/src/assets/law.json) | [649](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=649) |
| Mathematics and Astronomy<br />Mathématiques et Astronomie<br />Mathematik und Astronomie | الرياضيات والفلك | 4068 | [web](https://forzagreen.github.io/arabterm/mathematics_astronomy), [csv](data/mathematics_astronomy.csv), [json](website/src/assets/mathematics_astronomy.json), [scan](https://archive.org/details/ARA1990ENAR) | [668](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=668) |
| Physics<br />Physique<br />Physik | الفيزياء | 6315 | [web](https://forzagreen.github.io/arabterm/physics), [csv](data/physics.csv), [json](website/src/assets/physics.json), [scan](https://archive.org/details/Ara1989ENFRAR) | [669](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=669) |
| Chemistry<br />Chimie<br />Chemie | الكيمياء | 4532 | [web](https://forzagreen.github.io/arabterm/chemistry), [csv](data/chemistry.csv), [json](website/src/assets/chemistry.json) | [670](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=670) |
| Geology<br />Géologie<br />Geologie | الجيولوجيا | 4623 | [web](https://forzagreen.github.io/arabterm/geology), [csv](data/geology.csv), [json](website/src/assets/geology.json) | [671](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=671) |
| Seismology<br />Séismologie<br />Seismologie | علم الزلازل | 4722 | [web](https://forzagreen.github.io/arabterm/seismology), [csv](data/seismology.csv), [json](website/src/assets/seismology.json) | [672](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=672) |
| Meteorology<br />Météorologie<br />Meteorologie | الأرصاد الجوية | 2031 | [web](https://forzagreen.github.io/arabterm/meteorology), [csv](data/meteorology.csv), [json](website/src/assets/meteorology.json) | [673](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=673) |
| Oceanology<br />Océanographie<br />Ozeanographie | علوم البحار | 3913 | [web](https://forzagreen.github.io/arabterm/oceanology), [csv](data/oceanology.csv), [json](website/src/assets/oceanology.json) | [674](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=674) |
| Petroleum<br />Pétrole<br />Erdöl | النفط | 6089 | [web](https://forzagreen.github.io/arabterm/petroleum), [csv](data/petroleum.csv), [json](website/src/assets/petroleum.json) | [675](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=675) |
| Biology<br />Biologie<br />Biologie | علم الأحياء | 6561 | [web](https://forzagreen.github.io/arabterm/biology), [csv](data/biology.csv), [json](website/src/assets/biology.json) | [676](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=676) |
| Hygienics and Human Body<br />Santé et Corps Humain<br />Hygiene und Menschlicher Körper | الصحة وجسم الإنسان | 2134 | [web](https://forzagreen.github.io/arabterm/hygienics_human_body), [csv](data/hygienics_human_body.csv), [json](website/src/assets/hygienics_human_body.json), [scan](https://archive.org/details/BUR1992ENFRAR) | [677](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=677) |
| Genetics<br />Génétique<br />Genetik | علم الوراثة | 2542 | [web](https://forzagreen.github.io/arabterm/genetics), [csv](data/genetics.csv), [json](website/src/assets/genetics.json) | [678](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=678) |
| Pharmacy<br />Pharmacie<br />Pharmazeutik | علم الصيدلة | 3686 | [web](https://forzagreen.github.io/arabterm/pharmacy), [csv](data/pharmacy.csv), [json](website/src/assets/pharmacy.json) | [716](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=716) |
| Electronic Warfare<br />Guerre éléctronique<br />Elektronische Kriegführung | الحرب الإلكترونية | 1021 | [web](https://forzagreen.github.io/arabterm/electronic_warfare), [csv](data/electronic_warfare.csv), [json](website/src/assets/electronic_warfare.json) | [717](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=717) |
| Remote Sensing<br />Télédétection<br />Fernerkundung | الاستشعار عن بعد | 1196 | [web](https://forzagreen.github.io/arabterm/remote_sensing), [csv](data/remote_sensing.csv), [json](website/src/assets/remote_sensing.json) | [718](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=718) |
| Veterinary Medicine<br />Médecine Vétérinaire<br />Veterinärmedizin | الطب البيطري | 2741 | [web](https://forzagreen.github.io/arabterm/veterinary_medicine), [csv](data/veterinary_medicine.csv), [json](website/src/assets/veterinary_medicine.json) | [720](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=720) |
| Gross Anatomy<br />Anatomie Macroscopique<br />Mikroskopische Anatomie | التشريح العياني | 5779 | [web](https://forzagreen.github.io/arabterm/gross_anatomy), [csv](data/gross_anatomy.csv), [json](website/src/assets/gross_anatomy.json) | [721](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=721) |
| Masonry - Carpentry<br />Maçonnerie - Charpenterie<br />Maurerhandwerk - Zimmerhandwerk | البناء - النجارة | 3731 | [web](https://forzagreen.github.io/arabterm/masonry_carpentry), [csv](data/masonry_carpentry.csv), [json](website/src/assets/masonry_carpentry.json) | [727](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=727) |
| Printing - Electricity<br />Imprimerie - Electricité<br />Buchdruck - Elektrizität | الطباعة - الكهرباء | 2838 | [web](https://forzagreen.github.io/arabterm/printing_electricity), [csv](data/printing_electricity.csv), [json](website/src/assets/printing_electricity.json) | [728](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=728) |
| Nutrition Technologies<br />Technologies Alimentaires<br />Nahrungsmitteltechnologie | تقانات الأغذية | 2686 | [web](https://forzagreen.github.io/arabterm/nutrition_technologies), [csv](data/nutrition_technologies.csv), [json](website/src/assets/nutrition_technologies.json) | [729](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=729) |
| Information and Communication<br />Information et Communication<br />Information und Kommunikation | الإعلام والتواصل | 6081 | [web](https://forzagreen.github.io/arabterm/information_communication), [csv](data/information_communication.csv), [json](website/src/assets/information_communication.json) | [780](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=780) |
| Philosophy and Psychology<br />Philosophie et Psychologie<br />Philosophie und Psychologie | الفلسفة وعلم النفس | 1350 | [web](https://forzagreen.github.io/arabterm/philosophy_psychology), [csv](data/philosophy_psychology.csv), [json](website/src/assets/philosophy_psychology.json) | [781](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=781) |
| Arts, Recreation and Sports<br />Art, Divertissement et sports<br />Kunst, Vergnügung und Sport | الفن، التسلية والرياضة | 5269 | [web](https://forzagreen.github.io/arabterm/arts_recreation_sports), [csv](data/arts_recreation_sports.csv), [json](website/src/assets/arts_recreation_sports.json), [scan](https://archive.org/details/Ara1992ENAR) | [782](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=782) |
| Language and Literature<br />Langue et Littérature<br />Sprache und Literatur | اللغة والأدب | 3223 | [web](https://forzagreen.github.io/arabterm/language_literature), [csv](data/language_literature.csv), [json](website/src/assets/language_literature.json), [scan](https://archive.org/details/20200723_20200723_1608) | [783](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=783) |
| Geography and History<br />Géographie et Histoire<br />Geographie und Geschichte | الجغرافيا والتاريخ | 5724 | [web](https://forzagreen.github.io/arabterm/geography_history), [csv](data/geography_history.csv), [json](website/src/assets/geography_history.json), [scan](https://archive.org/details/BUR1994ENFRAR) | [784](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=784) |

<!-- 
782 (arts_recreation_sports) => موسيقى
783 (language_literature) => لسانيات
784 (geography_history) => جغرافيا
 -->

## References

- [https://forzagreen.github.io/arabterm/](https://forzagreen.github.io/arabterm/)
- [arabterm.org](http://www.arabterm.org)
- [مكتب تنسيق التعريب](http://www.arabization.org.ma/)
- [ويكيبيديا:مصادر موثوقة/معاجم وقواميس وأطالس](https://ar.wikipedia.org/wiki/%D9%88%D9%8A%D9%83%D9%8A%D8%A8%D9%8A%D8%AF%D9%8A%D8%A7:%D9%85%D8%B5%D8%A7%D8%AF%D8%B1_%D9%85%D9%88%D8%AB%D9%88%D9%82%D8%A9/%D9%85%D8%B9%D8%A7%D8%AC%D9%85_%D9%88%D9%82%D9%88%D8%A7%D9%85%D9%8A%D8%B3_%D9%88%D8%A3%D8%B7%D8%A7%D9%84%D8%B3)
 
