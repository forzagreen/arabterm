import Database from 'better-sqlite3';
import { resolve } from 'node:path';

// astro is always invoked from website/, so the DB sits one level up.
const DB_PATH = resolve(process.cwd(), '../arabterm.db');

export const PER_PAGE = 1000;

export interface Dictionary {
  id: number;
  name_tech: string;
  name_arabic: string;
  name_english: string | null;
  name_french: string | null;
  nbr_entries: number | null;
  wikidata_id: string | null;
  term_count: number;
}

export interface Term {
  id: number;
  arabic: string | null;
  english: string | null;
  french: string | null;
  description: string | null;
  uri: string | null;
}

let _db: Database.Database | null = null;
function db(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
  }
  return _db;
}

export function getAllDictionaries(): Dictionary[] {
  return db()
    .prepare(
      `SELECT d.id, d.name_tech, d.name_arabic, d.name_english, d.name_french,
              d.nbr_entries, d.wikidata_id,
              (SELECT COUNT(*) FROM term WHERE dictionary_id = d.id) AS term_count
         FROM dictionary d
         ORDER BY d.created_at DESC, d.id DESC`
    )
    .all() as Dictionary[];
}

export function getDictionary(nameTech: string): Dictionary | null {
  const row = db()
    .prepare(
      `SELECT d.id, d.name_tech, d.name_arabic, d.name_english, d.name_french,
              d.nbr_entries, d.wikidata_id,
              (SELECT COUNT(*) FROM term WHERE dictionary_id = d.id) AS term_count
         FROM dictionary d
        WHERE d.name_tech = ?`
    )
    .get(nameTech);
  return (row as Dictionary | undefined) ?? null;
}

export function getTermsPage(
  nameTech: string,
  page: number,
  perPage: number = PER_PAGE
): Term[] {
  const offset = (page - 1) * perPage;
  return db()
    .prepare(
      `SELECT t.id, t.arabic, t.english, t.french, t.description, t.uri
         FROM term t
         JOIN dictionary d ON d.id = t.dictionary_id
        WHERE d.name_tech = ?
        ORDER BY t.id
        LIMIT ? OFFSET ?`
    )
    .all(nameTech, perPage, offset) as Term[];
}

export function getAllTerms(nameTech: string): Term[] {
  return db()
    .prepare(
      `SELECT t.id, t.arabic, t.english, t.french, t.description, t.uri
         FROM term t
         JOIN dictionary d ON d.id = t.dictionary_id
        WHERE d.name_tech = ?
        ORDER BY t.id`
    )
    .all(nameTech) as Term[];
}

export function totalPages(termCount: number, perPage: number = PER_PAGE): number {
  return Math.max(1, Math.ceil(termCount / perPage));
}

// Legacy unprefixed slugs from the previous Angular site. Every legacy slug
// maps to `at_<slug>` in the current DB.
export const LEGACY_SLUGS = [
  'automotive_engineering',
  'water_engineering',
  'renewable_energy',
  'electrical_engineering',
  'transport_infrastructure',
  'textiles_industries',
  'civil_engineering',
  'information_tech',
  'climate_environment',
  'educational_techniques',
  'education',
  'sociology_anthropology',
  'economics',
  'commerce_accounting',
  'law',
  'mathematics_astronomy',
  'physics',
  'chemistry',
  'geology',
  'seismology',
  'meteorology',
  'oceanology',
  'petroleum',
  'biology',
  'hygienics_human_body',
  'genetics',
  'pharmacy',
  'electronic_warfare',
  'remote_sensing',
  'veterinary_medicine',
  'gross_anatomy',
  'masonry_carpentry',
  'printing_electricity',
  'nutrition_technologies',
  'information_communication',
  'philosophy_psychology',
  'arts_recreation_sports',
  'language_literature',
  'geography_history',
] as const;

export function legacyToNameTech(slug: string): string {
  return `at_${slug}`;
}
