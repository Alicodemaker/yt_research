import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// BASE_PATH is set by the GitHub Pages workflow (e.g. "/appstarter/").
// Locally it defaults to "/". Every URL below is derived from it, so the
// app, manifest and service worker all work under the repo subpath.
const base = process.env.BASE_PATH || '/'

// Content-Security-Policy for the built app: it may only run its own files and
// only talk to itself, so injected code can't send data anywhere else. Add each
// new network host to connect-src (or the matching directive), or its calls are
// silently blocked. Build only: the dev server needs inline styles for hot reload.
const csp = [
  "default-src 'self'",
  "connect-src 'self'",
  "img-src 'self' data:",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
].join('; ')

const contentSecurityPolicy = {
  name: 'content-security-policy',
  apply: 'build',
  transformIndexHtml: () => [
    { tag: 'meta', attrs: { 'http-equiv': 'Content-Security-Policy', content: csp }, injectTo: 'head-prepend' },
  ],
}

export default defineConfig({
  base,
  plugins: [
    contentSecurityPolicy,
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      includeAssets: ['icon.svg'],
      manifest: {
        name: 'App Starter',
        short_name: 'Starter',
        description: 'Mobile-first PWA starter',
        start_url: base,
        scope: base,
        display: 'standalone',
        orientation: 'portrait',
        // Keep in sync with --color-bg / --color-primary in src/theme.css
        background_color: '#ffffff',
        theme_color: '#1f6feb',
        icons: [
          { src: 'icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // Precache the whole build so the app works offline.
        globPatterns: ['**/*.{js,css,html,svg,png,ico,webmanifest,woff2}'],
        navigateFallback: 'index.html',
      },
    }),
  ],
})
