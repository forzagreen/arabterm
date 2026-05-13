import type { APIRoute, GetStaticPaths } from 'astro';
import { getAllDictionaries, getAllTerms } from '../../lib/db';

export const getStaticPaths: GetStaticPaths = () => {
  const dicts = getAllDictionaries();
  return dicts.map((d) => ({
    params: { dict: d.name_tech },
    props: { name_tech: d.name_tech, name_arabic: d.name_arabic, term_count: d.term_count },
  }));
};

export const GET: APIRoute = ({ props }) => {
  const { name_tech, name_arabic, term_count } = props as {
    name_tech: string;
    name_arabic: string;
    term_count: number;
  };
  const terms = getAllTerms(name_tech);
  const payload = {
    dictionary: { name_tech, name_arabic, term_count },
    terms,
  };
  return new Response(JSON.stringify(payload), {
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'content-disposition': `attachment; filename="${name_tech}.json"`,
    },
  });
};
