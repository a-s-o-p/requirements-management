const forms = require('@tailwindcss/forms');
const flowbitePlugin = require('flowbite/plugin');

module.exports = {
  content: [
    './index.html',
    './src/**/*.{svelte,js,ts}',
    './node_modules/flowbite-svelte/**/*.{svelte,js,ts}',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a'
        }
      }
    }
  },
  plugins: [forms, flowbitePlugin]
};
