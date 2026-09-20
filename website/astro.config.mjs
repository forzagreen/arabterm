import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://forzagreen.github.io',
  base: '/arabterm/',
  // 'ignore' instead of 'always' so .json endpoints (which can't have a trailing
  // slash) work in dev. HTML pages still ship as /foo/ via build.format: directory.
  trailingSlash: 'ignore',
  output: 'static',
  // Astro 7 defaults to 'jsx', which drops a line break next to an element or
  // an {expression} instead of collapsing it to a space. The templates wrap
  // Arabic sentences across lines, so that glues words together
  // ("10000من أصل"). `true` is the lossless behaviour Astro 6 had.
  compressHTML: true,
  build: {
    format: 'directory',
  },
  vite: {
    ssr: {
      external: ['better-sqlite3'],
    },
  },
});
