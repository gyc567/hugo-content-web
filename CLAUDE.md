# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Hugo Development
```bash
# Start development server with drafts enabled
hugo server -D

# Start development server with detailed output
hugo server -D --disableFastRender

# Build for production with minification
hugo --minify

# Clean build cache
hugo --gc

# Create new content
hugo new posts/my-new-post.md
hugo new about.md
```

### Deployment Commands
```bash
# Netlify deployment (configured in netlify.toml)
hugo --minify

# Vercel deployment
hugo --minify

# GitHub Pages (via GitHub Actions)
# Uses peaceiris/actions-hugo workflow
```

## Architecture Overview

### Core Technologies
- **Static Site Generator**: Hugo (Go-based)
- **Frontend**: Vanilla ES6+ JavaScript, Custom CSS with CSS Variables
- **Search**: Client-side JSON index generated at build time
- **Storage**: LocalStorage for user preferences and article likes
- **Ads**: Monetag integration for advertising revenue
- **SEO**: Comprehensive meta tags, Open Graph, structured data

### Key Components

#### JavaScript Architecture
- **SearchManager** (`static/js/search.js`): Client-side search with real-time results
- **LikesManager** (`static/js/likes.js`): Article like system with localStorage persistence
- **Main** (`static/js/main.js`): Mobile navigation and core UI interactions

#### CSS Architecture
- CSS Custom Properties for theming in `:root`
- Mobile-first responsive design
- Component-based styling structure

#### Hugo Templates
- **Base Template** (`themes/custom-theme/layouts/_default/baseof.html`): Main HTML structure
- **Search Index** (`layouts/index.json`): Generates JSON search index
- **Partial Components**: Header, footer, monetag ads in `partials/`

### Content Structure
- **Posts**: Markdown files in `content/posts/`
- **Pages**: Static pages in `content/` (about.md, search.md)
- **Assets**: CSS/JS in `static/`, images in `static/images/`
- **Theme**: Custom theme in `themes/custom-theme/`

## Development Patterns

### JavaScript Patterns
- ES6+ classes for feature management
- Event delegation for dynamic content
- LocalStorage abstraction for data persistence
- Modular architecture with clear separation of concerns

### CSS Patterns
- CSS Custom Properties for theming
- BEM-like naming conventions
- Mobile-first responsive breakpoints
- Component-scoped styles

### Hugo Patterns
- Custom shortcodes for reusable components
- Partial templates for shared UI elements
- JSON output formats for API-like endpoints
- Conditional feature flags in config

## Feature Configuration

### Search Configuration
- Enabled via `search_enabled = true` in hugo.toml
- Index generated at build time in `layouts/index.json`
- Client-side search in `static/js/search.js`

### Likes Configuration
- Enabled via `likes_enabled = true` in hugo.toml
- Storage config: `likes_storage = "localStorage"` (or "api")
- Client-side implementation in `static/js/likes.js`

### Monetag Configuration
- Enabled via `monetag_enabled = true` in hugo.toml
- Site ID: `monetag_site_id = "YOUR_SITE_ID"`
- Ad placements via partials and shortcodes

## Build Output
- Production build outputs to `public/` directory
- Search index available at `/index.json`
- Static assets minified and optimized
- Sitemap and robots.txt generated automatically

## Testing Approach
- Manual browser testing for UI components
- Validate search functionality with real content
- Test like system across page navigation
- Verify Monetag ad loading and placement
- Cross-browser compatibility testing

## Common Development Tasks

### Adding New Features
1. Add configuration option to `hugo.toml`
2. Implement JavaScript class in `static/js/`
3. Add CSS styles in `static/css/main.css`
4. Create Hugo partials if needed
5. Update documentation in README.md

### Content Creation
1. Use `hugo new posts/filename.md` for new posts
2. Front matter follows existing patterns
3. Include appropriate meta tags and images
4. Test search indexing and display

### Theme Customization
1. Modify `static/css/main.css` for styling
2. Update templates in `themes/custom-theme/layouts/`
3. Add new partials in `themes/custom-theme/layouts/partials/`
4. Create custom shortcodes in `layouts/shortcodes/`

Code Architecture Guidelines

────────────────────────────────────────
📏 Hard Requirements (MUST-FOLLOW)
────────────────────────────────────────
✅ Source-File Length Limits
• Dynamic languages (Python, JavaScript, TypeScript, etc.):  
  – **≤ 200 physical lines per file**  
• Static languages (Java, Go, Rust, etc.):  
  – **≤ 250 physical lines per file**  
> Purpose: improve readability, maintainability and reduce cognitive load.

✅ Directory Structure Limits
• **≤ 8 files per directory**  
• If exceeded, refactor into nested sub-directories.  
> Purpose: enhance structural clarity and enable rapid navigation and extension.

────────────────────────────────────────
🧠 Architectural Design Watch-List
────────────────────────────────────────
The following “smells” erode code quality and **must be vigilantly prevented**:

❌ 1. Rigidity  
> System becomes resistant to change; minor edits trigger cascading effects.  
Problem: high change-cost → low productivity.  
Mitigation: introduce interface abstraction, Strategy pattern, Dependency Inversion Principle.

❌ 2. Redundancy  
> Identical logic repeated in multiple places.  
Problem: code bloat & inconsistency.  
Mitigation: extract common functions/classes; favor composition over inheritance.

❌ 3. Circular Dependency  
> Modules mutually depend on each other, forming a deadlock.  
Problem: hinders testing, reuse and maintenance.  
Mitigation: decouple via interfaces, event mechanism, or dependency injection.

❌ 4. Fragility  
> Altering one area breaks seemingly unrelated parts.  
Problem: instability & frequent regressions.  
Mitigation: apply Single-Responsibility Principle and increase module cohesion.

❌ 5. Obscurity  
> Code structure is chaotic and intent is unclear.  
Problem: steep onboarding curve & collaboration friction.  
Mitigation: clear naming, concise comments, simple structure, up-to-date docs.

❌ 6. Data Clump  
> Several parameters always travel together, signaling a missing abstraction.  
Problem: bloated parameter lists & weak semantics.  
Mitigation: encapsulate into a data structure or value object.

❌ 7. Needless Complexity  
> Over-engineering—applying a heavyweight solution to a trivial problem.  
Problem: high comprehension & maintenance overhead.  
Mitigation: follow YAGNI and KISS; design only for proven needs.

────────────────────────────────────────
🚨 Critical Reminder
────────────────────────────────────────
> **CRITICAL:** When writing, reading or reviewing code, you **must** strictly adhere to the above hard limits and continuously evaluate architectural quality.

> **CRITICAL:** Upon detecting any smell, immediately prompt the user to consider refactoring and supply concrete optimization recommendations.

