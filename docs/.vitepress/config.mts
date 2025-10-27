import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "South Africa Customisations",
  description: "Country Specific Functionality for South Africa",
  outDir: '../csf_za/www',
  assetsDir: 'assets/csf_za',
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Desk', link: '/' },
      { text: 'Documentation Home', link: '/csf_za_introduction' },
      { text: 'Starktail', link: 'https://starktail.com' }
    ],

    sidebar: [
      { text: 'Introduction', link: '/csf_za_introduction' },
      { text: 'Value-added Tax Return', link: '/csf_za_value_added_tax_return.md' },
      { text: 'Support for Bank Statements from South African Banks', link: '/csf_za_bank_statement_import.md' },
      { text: 'Easy-add of VAT in Bank Reconciliation Tool', link: '/csf_za_bank_recon_tool.md' }
    ],

    socialLinks: [
      { icon: 'mailgun', link: 'mailto:support@starktail.com'},
      { icon: 'github', link: 'https://github.com/dvdl16/csf_za' }
    ],

    editLink: {
      pattern: 'https://github.com/dvdl16/csf_za/edit/version-15/docs/:path'
    }
  },
  // Set metaChunk to avoid having window.__VP_HASH_MAP__ in the generated HTML, 
  // as this blocks jinja template rendering for frappe portal pages
  metaChunk: true,
  ignoreDeadLinks: [
    // ignore all links starting with /app/ (these point to doctypes or other resources
    //  hosted on the frappe site, and won't be alive at build time)
    /^\/app\//
  ],
  // Links that point to pages outside our vitepress docs, like Doctype links should not
  // be appended with .html
  transformHtml: (code) => {
    return code.replace(/href="(\/app\/[^"]*)\.html"/g, 'href="$1"');
  },
  // Inline ALL images to avoid having images in the public directory
  vite: {
    build: {
      assetsInlineLimit: 52428800, // 50 MB,
      chunkSizeWarningLimit: 2000 // 2000 KB
    },
  },
})