export interface Dictionary {
  id: number;
  name: string;
  english: string;
  type: string;
  french: string;
  arabic: string;
  german: string;
  nbr_entries: number;
  available_languages: string[];
}

export const dictionaries = [
  {
    "id": 1,
    "english": "Automotive Engineering",
    "type": "Category",
    "french": "Technique automobile",
    "arabic": "هندسة وتكنولوجيا السيارات",
    "german": "Kfz-Technik",
    "nbr_entries": 4605,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "automotive_engineering"
  },
  {
    "id": 2,
    "english": "Water Engineering",
    "type": "Category",
    "french": "Technologie de l’eau",
    "arabic": "هندسة المياه",
    "german": "Wassertechnik",
    "nbr_entries": 8644,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "water_engineering"
  },
  {
    "id": 22,
    "english": "Renewable Energy",
    "type": "Category",
    "french": "Energies Renouvelables",
    "arabic": "الطاقات المتجددة",
    "german": "Erneuerbare Energien",
    "nbr_entries": 7289,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "renewable_energy"
  },
  {
    "id": 26,
    "english": "Electrical Engineering",
    "type": "Category",
    "french": "Génie Electrique",
    "arabic": "الهندسة الكهربائية",
    "german": "Elektrotechnik",
    "nbr_entries": 2569,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "electrical_engineering"
  },
  {
    "id": 30,
    "english": "Transport and Infrastructure",
    "type": "Category",
    "french": "Transport et Infrastructure",
    "arabic": "النقل والبنية التحتية",
    "german": "Transport und Infrastruktur",
    "nbr_entries": 5558,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "transport_infrastructure"
  },
  {
    "id": 34,
    "english": "Textiles Industries",
    "type": "Category",
    "french": "l’Industrie Textile",
    "arabic": "صناعة النسيج",
    "german": "Textilindustrie",
    "nbr_entries": 4513,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "textiles_industries"
  },
  {
    "id": 39,
    "english": "Civil Engineering",
    "type": "Category",
    "french": "Génie Civil",
    "arabic": "الهندسة المدنية",
    "german": "Bauingenieurwesen",
    "nbr_entries": 3943,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "civil_engineering"
  },
  {
    "id": 47,
    "english": "Information and Communication",
    "type": "Category",
    "french": "Technologie de l’Information",
    "arabic": "تقانة المعلومات",
    "german": "Informationstechnologie",
    "nbr_entries": 1369,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "information_tech"
  },
  {
    "id": 51,
    "english": "Climate, Environment and Solid Waste management",
    "type": "Category",
    "french": "Climat, l’Environment, et la Gestion des déchets solides",
    "arabic": "المناخ و البيئة و إدارة النفايات الصلبة",
    "german": "Klima, Umwelt und Abfallwirtschaft",
    "nbr_entries": 7040,
    "available_languages": [
      "arabic",
      "english",
      "french",
      "german"
    ],
    "name": "climate_environment"
  },
  {
    "id": 644,
    "english": "Educational and Computer Techniques",
    "type": "SubCategory",
    "french": "Techniques Pédagogiques et Informatiques",
    "arabic": "التقنيات التربوية والحاسوبية",
    "german": "Pädagogik und Informatiktechniken",
    "nbr_entries": 1524,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "educational_techniques"
  },
  {
    "id": 645,
    "english": "Education",
    "type": "SubCategory",
    "french": "Education",
    "arabic": "التربية",
    "german": "Erziehungswissenschaft",
    "nbr_entries": 2988,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "education"
  },
  {
    "id": 646,
    "english": "Sociology and Anthropology",
    "type": "SubCategory",
    "french": "Sociologie et Anthropologie",
    "arabic": "علم الاجتماع والأنثروبولوجيا",
    "german": "Soziologie und Anthropologie",
    "nbr_entries": 1261,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "sociology_anthropology"
  },
  {
    "id": 647,
    "english": "Economics",
    "type": "SubCategory",
    "french": "Economie",
    "arabic": "الاقتصاد",
    "german": "Wirtschaft",
    "nbr_entries": 2036,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "economics"
  },
  {
    "id": 648,
    "english": "Commerce and Accounting",
    "type": "SubCategory",
    "french": "Commerce et Comptabilité",
    "arabic": "التجارة والمحاسبة",
    "german": "Handel und Rechnungswesen",
    "nbr_entries": 8862,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "commerce_accounting"
  },
  {
    "id": 649,
    "english": "Law",
    "type": "SubCategory",
    "french": "Droit",
    "arabic": "القانون",
    "german": "Rechtswissenschaft",
    "nbr_entries": 3218,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "law"
  },
  {
    "id": 668,
    "english": "Mathematics and Astronomy",
    "type": "SubCategory",
    "french": "Mathématiques et Astronomie",
    "arabic": "الرياضيات والفلك",
    "german": "Mathematik und Astronomie",
    "nbr_entries": 4068,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "mathematics_astronomy"
  },
  {
    "id": 669,
    "english": "Physics",
    "type": "SubCategory",
    "french": "Physique",
    "arabic": "الفيزياء",
    "german": "Physik",
    "nbr_entries": 6315,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "physics"
  },
  {
    "id": 670,
    "english": "Chemistry",
    "type": "SubCategory",
    "french": "Chimie",
    "arabic": "الكيمياء",
    "german": "Chemie",
    "nbr_entries": 4532,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "chemistry"
  },
  {
    "id": 671,
    "english": "Geology",
    "type": "SubCategory",
    "french": "Géologie",
    "arabic": "الجيولوجيا",
    "german": "Geologie",
    "nbr_entries": 4623,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "geology"
  },
  {
    "id": 672,
    "english": "Seismology",
    "type": "SubCategory",
    "french": "Séismologie",
    "arabic": "علم الزلازل",
    "german": "Seismologie",
    "nbr_entries": 4722,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "seismology"
  },
  {
    "id": 673,
    "english": "Meteorology",
    "type": "SubCategory",
    "french": "Météorologie",
    "arabic": "الأرصاد الجوية",
    "german": "Meteorologie",
    "nbr_entries": 2031,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "meteorology"
  },
  {
    "id": 674,
    "english": "Oceanology",
    "type": "SubCategory",
    "french": "Océanographie",
    "arabic": "علوم البحار",
    "german": "Ozeanographie",
    "nbr_entries": 3913,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "oceanology"
  },
  {
    "id": 675,
    "english": "Petroleum",
    "type": "SubCategory",
    "french": "Pétrole",
    "arabic": "النفط",
    "german": "Erdöl",
    "nbr_entries": 6089,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "petroleum"
  },
  {
    "id": 676,
    "english": "Biology",
    "type": "SubCategory",
    "french": "Biologie",
    "arabic": "علم الأحياء",
    "german": "Biologie",
    "nbr_entries": 6561,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "biology"
  },
  {
    "id": 677,
    "english": "Hygienics and Human Body",
    "type": "SubCategory",
    "french": "Santé et Corps Humain",
    "arabic": "الصحة وجسم الإنسان",
    "german": "Hygiene und Menschlicher Körper",
    "nbr_entries": 2134,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "hygienics_human_body"
  },
  {
    "id": 678,
    "english": "Genetics",
    "type": "SubCategory",
    "french": "Génétique",
    "arabic": "علم الوراثة",
    "german": "Genetik",
    "nbr_entries": 2542,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "genetics"
  },
  {
    "id": 716,
    "english": "Pharmacy",
    "type": "SubCategory",
    "french": "Pharmacie",
    "arabic": "علم الصيدلة",
    "german": "Pharmazeutik",
    "nbr_entries": 3686,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "pharmacy"
  },
  {
    "id": 717,
    "english": "Electronic Warfare",
    "type": "SubCategory",
    "french": "Guerre éléctronique",
    "arabic": "الحرب الإلكترونية",
    "german": "Elektronische Kriegführung",
    "nbr_entries": 1021,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "electronic_warfare"
  },
  {
    "id": 718,
    "english": "Remote Sensing",
    "type": "SubCategory",
    "french": "Télédétection",
    "arabic": "الاستشعار عن بعد",
    "german": "Fernerkundung",
    "nbr_entries": 1196,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "remote_sensing"
  },
  {
    "id": 720,
    "english": "Veterinary Medicine",
    "type": "SubCategory",
    "french": "Médecine Vétérinaire",
    "arabic": "الطب البيطري",
    "german": "Veterinärmedizin",
    "nbr_entries": 2741,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "veterinary_medicine"
  },
  {
    "id": 721,
    "english": "Gross Anatomy",
    "type": "SubCategory",
    "french": "Anatomie Macroscopique",
    "arabic": "التشريح العياني",
    "german": "Mikroskopische Anatomie",
    "nbr_entries": 5779,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "gross_anatomy"
  },
  {
    "id": 727,
    "english": "Masonry - Carpentry",
    "type": "SubCategory",
    "french": "Maçonnerie - Charpenterie",
    "arabic": "البناء - النجارة",
    "german": "Maurerhandwerk - Zimmerhandwerk",
    "nbr_entries": 3731,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "masonry_carpentry"
  },
  {
    "id": 728,
    "english": "Printing - Electricity",
    "type": "SubCategory",
    "french": "Imprimerie - Electricité",
    "arabic": "الطباعة - الكهرباء",
    "german": "Buchdruck - Elektrizität",
    "nbr_entries": 2838,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "printing_electricity"
  },
  {
    "id": 729,
    "english": "Nutrition Technologies",
    "type": "SubCategory",
    "french": "Technologies Alimentaires",
    "arabic": "تقانات الأغذية",
    "german": "Nahrungsmitteltechnologie",
    "nbr_entries": 2686,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "nutrition_technologies"
  },
  {
    "id": 780,
    "english": "Information and Communication",
    "type": "SubCategory",
    "french": "Information et Communication",
    "arabic": "الإعلام والتواصل",
    "german": "Information und Kommunikation",
    "nbr_entries": 6081,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "information_communication"
  },
  {
    "id": 781,
    "english": "Philosophy and Psychology",
    "type": "SubCategory",
    "french": "Philosophie et Psychologie",
    "arabic": "الفلسفة وعلم النفس",
    "german": "Philosophie und Psychologie",
    "nbr_entries": 1350,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "philosophy_psychology"
  },
  {
    "id": 782,
    "english": "Arts, Recreation and Sports",
    "type": "SubCategory",
    "french": "Art, Divertissement et sports",
    "arabic": "الفن، التسلية والرياضة",
    "german": "Kunst, Vergnügung und Sport",
    "nbr_entries": 5269,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "arts_recreation_sports"
  },
  {
    "id": 783,
    "english": "Language and Literature",
    "type": "SubCategory",
    "french": "Langue et Littérature",
    "arabic": "اللغة والأدب",
    "german": "Sprache und Literatur",
    "nbr_entries": 3223,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "language_literature"
  },
  {
    "id": 784,
    "english": "Geography and History",
    "type": "SubCategory",
    "french": "Géographie et Histoire",
    "arabic": "الجغرافيا والتاريخ",
    "german": "Geographie und Geschichte",
    "nbr_entries": 5724,
    "available_languages": [
      "arabic",
      "english",
      "french"
    ],
    "name": "geography_history"
  }
]
