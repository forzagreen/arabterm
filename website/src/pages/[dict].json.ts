import type { APIRoute, GetStaticPaths } from 'astro';
import { getAllDictionaries, getAllTerms, type Domain } from '../lib/db';

export const getStaticPaths: GetStaticPaths = () => {
  const dicts = getAllDictionaries();
  return dicts.map((d) => ({
    params: { dict: d.name_tech },
    props: {
      name_tech: d.name_tech,
      name_arabic: d.name_arabic,
      term_count: d.term_count,
      // Without the internal id: the slug identifies a domain.
      domains: d.domains.map(({ id, ...domain }) => domain),
    },
  }));
};

export const GET: APIRoute = ({ props }) => {
  const { name_tech, name_arabic, term_count, domains } = props as {
    name_tech: string;
    name_arabic: string;
    term_count: number;
    domains: Omit<Domain, 'id'>[];
  };
  const terms = getAllTerms(name_tech);
  const payload = {
    dictionary: { name_tech, name_arabic, term_count, domains },
    terms,
  };
  return new Response(JSON.stringify(payload), {
    headers: {
      'content-type': 'application/json; charset=utf-8',
    },
  });
};
