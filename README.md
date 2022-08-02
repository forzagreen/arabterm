# arabterm


[Arab Term](http://www.arabterm.org/) is a set of multilingual technical dictionaries, organised by technical domains and industry sectors.

This repository provides a full extract of [arabterm.org](http://www.arabterm.org/) dictionaries, in CSV files and in a [SQLite](https://www.sqlite.org/) database.

The data extraction was performed between March and August of 2022, by web scraping [arabterm.org](http://www.arabterm.org/), using python, [Selenium](https://selenium-python.readthedocs.io/), and [lxml](https://lxml.de/lxmlhtml.html).


- [arabterm](#arabterm)
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


## Dictionaries

Click on the CSV link to see all technical terms of a given domain.

| ArabTerm page | Extract file | Number of entries | English | العربية | Français | Deutsch | Scan |
|---|---|---|---|---:|---|---|---|
| [1](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=1) | [automotive_engineering.csv](data/automotive_engineering.csv) | 4605 | Automotive Engineering | هندسة وتكنولوجيا السيارات | Technique automobile | Kfz-Technik |  |
| [2](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=2) | [water_engineering.csv](data/water_engineering.csv) | 8644 | Water Engineering | هندسة المياه | Technologie de l’eau | Wassertechnik |  |
| [22](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=22) | [renewable_energy.csv](data/renewable_energy.csv) | 7289 | Renewable Energy | الطاقات المتجددة | Energies Renouvelables | Erneuerbare Energien |  |
| [26](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=26) | [electrical_engineering.csv](data/electrical_engineering.csv) | 2569 | Electrical Engineering | الهندسة الكهربائية | Génie Electrique | Elektrotechnik |  |
| [30](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=30) | [transport_infrastructure.csv](data/transport_infrastructure.csv) | 5558 | Transport and Infrastructure | النقل والبنية التحتية | Transport et Infrastructure | Transport und Infrastruktur |  |
| [34](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=34) | [textiles_industries.csv](data/textiles_industries.csv) | 4513 | Textiles Industries | صناعة النسيج | l’Industrie Textile | Textilindustrie |  |
| [39](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=39) | [civil_engineering.csv](data/civil_engineering.csv) | 3943 | Civil Engineering | الهندسة المدنية | Génie Civil | Bauingenieurwesen |  |
| [47](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=47) | [information_tech.csv](data/information_tech.csv) | 1369 | Information and Communication | تقانة المعلومات | Technologie de l’Information | Informationstechnologie | [scan](https://archive.org/details/ALECSO2011AREN) |
| [51](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterCategory]=51) | [climate_environment.csv](data/climate_environment.csv) | 7040 | Climate, Environment and Solid Waste management | المناخ والبيئة وإدارة النفايات الصلبة | Climat, l’Environment, et la Gestion des déchets solides | Klima, Umwelt und Abfallwirtschaft |  |
| [644](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=644) | [educational_techniques.csv](data/educational_techniques.csv) | 1524 | Educational and Computer Techniques | التقنيات التربوية والحاسوبية | Techniques Pédagogiques et Informatiques | Pädagogik und Informatiktechniken |  |
| [645](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=645) | [education.csv](data/education.csv) | 2988 | Education | التربية | Education | Erziehungswissenschaft |  |
| [646](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=646) | [sociology_anthropology.csv](data/sociology_anthropology.csv) | 1261 | Sociology and Anthropology | علم الاجتماع والأنثروبولوجيا | Sociologie et Anthropologie | Soziologie und Anthropologie |  |
| [647](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=647) | [economics.csv](data/economics.csv) | 2036 | Economics | الاقتصاد | Economie | Wirtschaft |  |
| [648](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=648) | [commerce_accounting.csv](data/commerce_accounting.csv) | 8862 | Commerce and Accounting | التجارة والمحاسبة | Commerce et Comptabilité | Handel und Rechnungswesen |  |
| [649](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=649) | [law.csv](data/law.csv) | 3218 | Law | القانون | Droit | Rechtswissenschaft |  |
| [668](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=668) | [mathematics_astronomy.csv](data/mathematics_astronomy.csv) | 4068 | Mathematics and Astronomy | الرياضيات والفلك | Mathématiques et Astronomie | Mathematik und Astronomie |  |
| [669](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=669) | [physics.csv](data/physics.csv) | 6315 | Physics | الفيزياء | Physique | Physik |  |
| [670](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=670) | [chemistry.csv](data/chemistry.csv) | 4532 | Chemistry | الكيمياء | Chimie | Chemie |  |
| [671](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=671) | [geology.csv](data/geology.csv) | 4623 | Geology | الجيولوجيا | Géologie | Geologie |  |
| [672](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=672) | [seismology.csv](data/seismology.csv) | 4722 | Seismology | علم الزلازل | Séismologie | Seismologie |  |
| [673](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=673) | [meteorology.csv](data/meteorology.csv) | 2031 | Meteorology | الأرصاد الجوية | Météorologie | Meteorologie |  |
| [674](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=674) | [oceanology.csv](data/oceanology.csv) | 3913 | Oceanology | علوم البحار | Océanographie | Ozeanographie |  |
| [675](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=675) | [petroleum.csv](data/petroleum.csv) | 6089 | Petroleum | النفط | Pétrole | Erdöl |  |
| [676](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=676) | [biology.csv](data/biology.csv) | 6561 | Biology | علم الأحياء | Biologie | Biologie |  |
| [677](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=677) | [hygienics_human_body.csv](data/hygienics_human_body.csv) | 2134 | Hygienics and Human Body | الصحة وجسم الإنسان | Santé et Corps Humain | Hygiene und Menschlicher Körper |  |
| [678](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=678) | [genetics.csv](data/genetics.csv) | 2542 | Genetics | علم الوراثة | Génétique | Genetik |  |
| [716](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=716) | [pharmacy.csv](data/pharmacy.csv) | 3686 | Pharmacy | علم الصيدلة | Pharmacie | Pharmazeutik |  |
| [717](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=717) | [electronic_warfare.csv](data/electronic_warfare.csv) | 1021 | Electronic Warfare | الحرب الإلكترونية | Guerre éléctronique | Elektronische Kriegführung |  |
| [718](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=718) | [remote_sensing.csv](data/remote_sensing.csv) | 1196 | Remote Sensing | الاستشعار عن بعد | Télédétection | Fernerkundung |  |
| [720](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=720) | [veterinary_medicine.csv](data/veterinary_medicine.csv) | 2741 | Veterinary Medicine | الطب البيطري | Médecine Vétérinaire | Veterinärmedizin |  |
| [721](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=721) | [gross_anatomy.csv](data/gross_anatomy.csv) | 5779 | Gross Anatomy | التشريح العياني | Anatomie Macroscopique | Mikroskopische Anatomie |  |
| [727](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=727) | [masonry_carpentry.csv](data/masonry_carpentry.csv) | 3731 | Masonry - Carpentry | البناء - النجارة | Maçonnerie - Charpenterie | Maurerhandwerk - Zimmerhandwerk |  |
| [728](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=728) | [printing_electricity.csv](data/printing_electricity.csv) | 2838 | Printing - Electricity | الطباعة - الكهرباء | Imprimerie - Electricité | Buchdruck - Elektrizität |  |
| [729](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=729) | [nutrition_technologies.csv](data/nutrition_technologies.csv) | 2686 | Nutrition Technologies | تقانات الأغذية | Technologies Alimentaires | Nahrungsmitteltechnologie |  |
| [780](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=780) | [information_communication.csv](data/information_communication.csv) | 6081 | Information and Communication | الإعلام والتواصل | Information et Communication | Information und Kommunikation |  |
| [781](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=781) | [philosophy_psychology.csv](data/philosophy_psychology.csv) | 1350 | Philosophy and Psychology | الفلسفة وعلم النفس | Philosophie et Psychologie | Philosophie und Psychologie |  |
| [782](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=782) | [arts_recreation_sports.csv](data/arts_recreation_sports.csv) | 5269 | Arts, Recreation and Sports | الفن، التسلية والرياضة | Art, Divertissement et sports | Kunst, Vergnügung und Sport | [scan](https://archive.org/details/Ara1992ENAR) |
| [783](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=783) | [language_literature.csv](data/language_literature.csv) | 3223 | Language and Literature | اللغة والأدب | Langue et Littérature | Sprache und Literatur | [scan](https://archive.org/details/20200723_20200723_1608) |
| [784](http://arabterm.org/index.php?tx_3m5techdict_pi1[filterSubCategory]=784) | [geography_history.csv](data/geography_history.csv) | 5724 | Geography and History | الجغرافيا والتاريخ | Géographie et Histoire | Geographie und Geschichte |  |


## References

- [arabterm.org](http://www.arabterm.org)
- [مكتب تنسيق التعريب](http://www.arabization.org.ma/)
- [ويكيبيديا:مصادر موثوقة/معاجم وقواميس وأطالس](https://ar.wikipedia.org/wiki/%D9%88%D9%8A%D9%83%D9%8A%D8%A8%D9%8A%D8%AF%D9%8A%D8%A7:%D9%85%D8%B5%D8%A7%D8%AF%D8%B1_%D9%85%D9%88%D8%AB%D9%88%D9%82%D8%A9/%D9%85%D8%B9%D8%A7%D8%AC%D9%85_%D9%88%D9%82%D9%88%D8%A7%D9%85%D9%8A%D8%B3_%D9%88%D8%A3%D8%B7%D8%A7%D9%84%D8%B3)
 
