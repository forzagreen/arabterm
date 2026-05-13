import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://forzagreen.github.io',
  base: '/arabterm',
  trailingSlash: 'always',
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
