# Server-Side Web UI
New web UI for llamagrab which is server-side rendered.

### Built Using
- [htmx](https://htmx.org/) for interactivity
- [bulma](https://bulma.io/) for styles/layout
- [bootstrap-icons](https://icons.getbootstrap.com/)
- [Tagify](https://yaireo.github.io/tagify/)

```
yarn install

# Build css & deps once
yarn build

# for testing live css changes
yarn run dev
```

To work on templates, run api from project root
```
python3 -m api
```

## Notes

### Code

- `public/` - assets which are copied into `static/` at build time to be served
- `src/` - JS, SASS styles (compiled into `static/`)
- `templates/` - jinja templates sources rendered by llamagrab web server

#### Jinja templates vs macros

- Macros which are placed into `templates/macros/` are automatically loaded by the server and available globally to any templates without `{% import ... %}`. This supports multiple macros per file.
- Macros should manually `{% import %}` other macros
- Use macros for frequently repeated HTML patterns in templates
- Use templates for HTML sections which need to be returned directly by the web server
    - For examples `server_card` is sometimes rendered by a web endpoint, so it's a template
    - `icon` is never returned directly, and is used many times in other templates, so it  is a macro

#### Design/Guidelines

The design mostly on the CSS framework ([bulma](bulma.io)) with a minimal amount of styling/color scheme applied on top. Colors should be used sparingly to indicate actions or status.

All UI elements should be designed first for desktop use but should be responsive and usable on (rather than optimized-for) mobile. For small screens, breakpoints are used to hide less critical information, shorten/remove some text.

- Minimize custom CSS and JS. Prefer HTMX & bulma built-ins wherever possible
- Define base styling variables as `lg-*` in `base.scss`. Map bulma variables to those, such as `$primary = $lg-primary`. Use the bulma variables in styles instead of `lg-*`.

### Build Process
When you run `yarn run dev` or `yarn run build`:

- `sass/` is compiled to css and copied into `static/css`
- assets from `public/` are copied into `static/`
- bootstrap-icon fonts from `node_modules` are copied into `static/fonts`

`static/*` is served under `/static/*` by the api server.

