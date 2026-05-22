import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://forzagreen.github.io',
  base: '/arabterm/',
  // 'ignore' instead of 'always' so .json endpoints (which can't have a trailing
  // slash) work in dev. HTML pages still ship as /foo/ via build.format: directory.
  trailingSlash: 'ignore',
  output: 'static',
  build: {
    format: 'directory',
  },
  vite: {
    ssr: {
      external: ['better-sqlite3'],
    },
  },
});
