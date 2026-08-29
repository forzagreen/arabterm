import Database from 'better-sqlite3';
import { resolve } from 'node:path';

// astro is always invoked from website/, so the DB sits one level up.
const DB_PATH = resolve(process.cwd(), '../arabterm.db');

export const PER_PAGE = 1000;

/**
 * Which term columns are worth rendering for a given dictionary: a column is
 * kept only when at least one row in the *whole* dictionary fills it. Several
 * dictionaries have no French, no description or (al_mawrid) no Arabic at all,
 * and rendering those as a wall of empty cells wastes both screen and bytes.
 */
export interface TermColumns {
  arabic: boolean;
  english: boolean;
  french: boolean;
  description: boolean;
  page: boolean;
  uri: boolean;
}

export interface Dictionary {
  id: number;
  name_tech: string;
  name_arabic: string;
  name_english: string | null;
  name_french: string | null;
  nbr_entries: number | null;
  wikidata_id: string | null;
  term_count: number;
  cols: TermColumns;
}

export interface Term {
  id: number;
  arabic: string | null;
  english: string | null;
  french: string | null;
  description: string | null;
  page: number | null;
  uri: string | null;
}

interface DictionaryRow {
  id: number;
  name_tech: string;
  name_arabic: string;
  name_english: string | null;
  name_french: string | null;
  nbr_entries: number | null;
  wikidata_id: string | null;
  term_count: number;
  has_arabic: number | null;
  has_english: number | null;
  has_french: number | null;
  has_description: number | null;
  has_page: number | null;
  has_uri: number | null;
}

let _db: Database.Database | null = null;
function db(): Database.Database {
  if (!_db) {
    _db = new Database(DB_PATH, { readonly: true, fileMustExist: true });
  }
  return _db;
}

// One grouped pass over `term` yields both the row count and the per-column
// presence flags, so the whole site costs a single scan instead of one query
// per dictionary per column.
const DICT_SELECT = `
  SELECT d.id, d.name_tech, d.name_arabic, d.name_english, d.name_french,
         d.nbr_entries, d.wikidata_id,
         COUNT(t.id) AS term_count,
         MAX(t.arabic      IS NOT NULL AND t.arabic      <> '') AS has_arabic,
         MAX(t.english     IS NOT NULL AND t.english     <> '') AS has_english,
         MAX(t.french      IS NOT NULL AND t.french      <> '') AS has_french,
         MAX(t.description IS NOT NULL AND t.description <> '') AS has_description,
         MAX(t.page        IS NOT NULL)                         AS has_page,
         MAX(t.uri         IS NOT NULL AND t.uri         <> '') AS has_uri
    FROM dictionary d
    LEFT JOIN term t ON t.dictionary_id = d.id`;

function toDictionary(row: DictionaryRow): Dictionary {
  const { has_arabic, has_english, has_french, has_description, has_page, has_uri, ...rest } = row;
  return {
    ...rest,
    cols: {
      arabic: !!has_arabic,
      english: !!has_english,
      french: !!has_french,
      description: !!has_description,
      page: !!has_page,
      uri: !!has_uri,
    },
  };
}

export function getAllDictionaries(): Dictionary[] {
  const rows = db()
    .prepare(`${DICT_SELECT} GROUP BY d.id ORDER BY d.created_at DESC, d.id DESC`)
    .all() as DictionaryRow[];
  return rows.map(toDictionary);
}

export function getDictionary(nameTech: string): Dictionary | null {
  const row = db()
    .prepare(`${DICT_SELECT} WHERE d.name_tech = ? GROUP BY d.id`)
    .get(nameTech) as DictionaryRow | undefined;
  return row ? toDictionary(row) : null;
}

export function getTermsPage(
  nameTech: string,
  page: number,
  perPage: number = PER_PAGE
): Term[] {
  const offset = (page - 1) * perPage;
  return db()
    .prepare(
      `SELECT t.id, t.arabic, t.english, t.french, t.description, t.page, t.uri
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
      `SELECT t.id, t.arabic, t.english, t.french, t.description, t.page, t.uri
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
