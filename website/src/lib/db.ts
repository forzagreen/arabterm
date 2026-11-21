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

/**
 * A subject that dictionaries are about, shown as a tag: one value of "main
 * subject" (P921) on the dictionaries' Wikidata items, under a short name
 * («رياضيات» for the item «مصطلحات الرياضيات»).
 */
export interface Domain {
  id: number;
  name_tech: string;
  name_arabic: string;
  name_english: string | null;
  name_french: string | null;
  wikidata_id: string | null;
}

export interface Dictionary {
  id: number;
  name_tech: string;
  name_arabic: string;
  name_english: string | null;
  name_french: string | null;
  nbr_entries: number | null;
  wikidata_id: string | null;
  archive_org_url: string | null;
  page_offset: number | null;
  term_count: number;
  cols: TermColumns;
  // One or more; a dictionary on two subjects has both.
  domains: Domain[];
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
  archive_org_url: string | null;
  page_offset: number | null;
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
         d.nbr_entries, d.wikidata_id, d.archive_org_url, d.page_offset,
         COUNT(t.id) AS term_count,
         MAX(t.arabic      IS NOT NULL AND t.arabic      <> '') AS has_arabic,
         MAX(t.english     IS NOT NULL AND t.english     <> '') AS has_english,
         MAX(t.french      IS NOT NULL AND t.french      <> '') AS has_french,
         MAX(t.description IS NOT NULL AND t.description <> '') AS has_description,
         MAX(t.page        IS NOT NULL)                         AS has_page,
         MAX(t.uri         IS NOT NULL AND t.uri         <> '') AS has_uri
    FROM dictionary d
    LEFT JOIN term t ON t.dictionary_id = d.id`;

// The domains of every dictionary, read once per build: two small tables
// (a few dozen rows each), asked for by every dictionary of every page.
let _domainsOf: Map<number, Domain[]> | null = null;
function domainsOf(dictionaryId: number): Domain[] {
  if (!_domainsOf) {
    const rows = db()
      .prepare(
        `SELECT dd.dictionary_id, dm.id, dm.name_tech, dm.name_arabic, dm.name_english,
                dm.name_french, dm.wikidata_id
           FROM dictionary_domain dd
           JOIN domain dm ON dm.id = dd.domain_id
          ORDER BY dd.dictionary_id, dm.id`
      )
      .all() as (Domain & { dictionary_id: number })[];
    _domainsOf = new Map();
    for (const { dictionary_id, ...domain } of rows) {
      const list = _domainsOf.get(dictionary_id) ?? [];
      list.push(domain);
      _domainsOf.set(dictionary_id, list);
    }
  }
  return _domainsOf.get(dictionaryId) ?? [];
}

export interface DomainWithCount extends Domain {
  dict_count: number;
}

/** Every domain with the number of its dictionaries, the largest first. */
export function getAllDomains(): DomainWithCount[] {
  return db()
    .prepare(
      `SELECT dm.id, dm.name_tech, dm.name_arabic, dm.name_english, dm.name_french,
              dm.wikidata_id, COUNT(dd.dictionary_id) AS dict_count
         FROM domain dm
         JOIN dictionary_domain dd ON dd.domain_id = dm.id
        GROUP BY dm.id
        ORDER BY dict_count DESC, dm.id`
    )
    .all() as DomainWithCount[];
}

function toDictionary(row: DictionaryRow): Dictionary {
  const { has_arabic, has_english, has_french, has_description, has_page, has_uri, ...rest } = row;
  return {
    ...rest,
    domains: domainsOf(row.id),
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

/**
 * The page of the dictionary's archive.org scan that shows printed page
 * `page`, or null when there is no scan or no page. archive.org numbers the
 * pages of the file from 0 (`n0` is the first page), and the file page of
 * printed page p is p + page_offset (Wikidata's P8330).
 */
export function scanPageUrl(
  dict: Pick<Dictionary, 'archive_org_url' | 'page_offset'>,
  page: number | null
): string | null {
  if (!dict.archive_org_url || dict.page_offset === null || page === null) return null;
  const n = page + dict.page_offset - 1;
  return n < 0 ? dict.archive_org_url : `${dict.archive_org_url}/page/n${n}/mode/1up`;
}

export interface DictionaryIndexEntry {
  id: number;
  name_tech: string;
  name_arabic: string;
}

// Every dictionary by descending id, i.e. most recently added first, without
// the term counts: enough for the "what's new" panel, which every page
// carries. Computed once per build, so it costs nothing per page.
let _index: DictionaryIndexEntry[] | null = null;
export function getDictionaryIndex(): DictionaryIndexEntry[] {
  if (!_index) {
    _index = db()
      .prepare('SELECT id, name_tech, name_arabic FROM dictionary ORDER BY id DESC')
      .all() as DictionaryIndexEntry[];
  }
  return _index;
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

export type GuideLang = 'ar' | 'en' | 'fr';

export interface PageGuide {
  first: string;
  last: string;
}

/** The guide words of every page of a dictionary: `pages[0]` is page 1. */
export interface DictionaryGuide {
  lang: GuideLang;
  pages: PageGuide[];
}

// Below this share of adjacent terms in ascending order, a dictionary is not
// considered sorted in that language. Sorted dictionaries score 0.82 to 1.00
// (compound entries, accents and case keep them under 1), unsorted ones 0.50,
// and the few that are sorted block by block 0.65 to 0.76.
const SORTED_THRESHOLD = 0.8;

const _guides = new Map<string, DictionaryGuide | null>();

/**
 * Guide words, as at the top of the pages of a printed dictionary: the first
 * and the last term of each page, in the language the dictionary is sorted by.
 * They tell the reader which page holds the word they are after, which a page
 * number alone does not. Null when the dictionary is sorted in no language
 * (e.g. grouped by topic): the first and last term of a page then say nothing
 * about what lies in between.
 */
export function getPageGuides(
  dict: Pick<Dictionary, 'id' | 'name_tech'>,
  perPage: number = PER_PAGE
): DictionaryGuide | null {
  const key = `${dict.name_tech}:${perPage}`;
  const cached = _guides.get(key);
  if (cached !== undefined) return cached;

  const langs: { lang: GuideLang; col: 'arabic' | 'english' | 'french' }[] = [
    { lang: 'ar', col: 'arabic' },
    { lang: 'en', col: 'english' },
    { lang: 'fr', col: 'french' },
  ];
  const stats = langs.map(() => ({
    prev: null as string | null,
    ascending: 0,
    pairs: 0,
    pages: [] as PageGuide[],
  }));

  // One streamed pass per dictionary, cached: every page of the dictionary
  // asks for the same guides.
  const rows = db()
    .prepare('SELECT arabic, english, french FROM term WHERE dictionary_id = ? ORDER BY id')
    .iterate(dict.id) as IterableIterator<Record<'arabic' | 'english' | 'french', string | null>>;
  let i = 0;
  for (const row of rows) {
    const page = Math.floor(i / perPage);
    langs.forEach(({ col }, k) => {
      const st = stats[k];
      st.pages[page] ??= { first: '', last: '' };
      const value = (row[col] ?? '').trim();
      // A term without a value in this language is skipped: the guide word
      // is the nearest term that has one.
      if (!value) return;
      const folded = value.toLowerCase();
      if (st.prev !== null) {
        st.pairs++;
        if (st.prev <= folded) st.ascending++;
      }
      st.prev = folded;
      if (!st.pages[page].first) st.pages[page].first = value;
      st.pages[page].last = value;
    });
    i++;
  }

  let best: DictionaryGuide | null = null;
  let bestScore = SORTED_THRESHOLD;
  stats.forEach((st, k) => {
    const score = st.pairs ? st.ascending / st.pairs : 0;
    if (score >= bestScore) {
      bestScore = score;
      best = { lang: langs[k].lang, pages: st.pages };
    }
  });
  _guides.set(key, best);
  return best;
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
