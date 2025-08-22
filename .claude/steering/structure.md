# Project Structure - Hugo Content Web

## Directory Organization
```
hugo-content-web/
├── .claude/                 # Claude steering and spec documents
│   └── steering/            # Persistent project context
├── archetypes/              # Content templates
│   └── default.md           # Default front matter template
├── assets/                  # Source assets (processed by Hugo)
│   ├── js/                  # Source JavaScript files
│   └── scss/                # Source SCSS files (if used)
├── content/                 # Markdown content
│   ├── posts/               # Blog posts and articles
│   │   └── welcome.md       # Example post
│   ├── about.md             # About page
│   └── search.md            # Search results page
├── data/                    # Data files for templates
├── layouts/                 # Site-wide layouts and overrides
│   ├── _default/            # Default templates
│   ├── index.json           # Search index generator
│   ├── partials/            # Reusable components
│   ├── search/              # Search-specific templates
│   │   └── search.html      # Search results template
│   └── shortcodes/          # Custom shortcodes
├── static/                  # Static assets (copied directly)
│   ├── css/                 # Compiled CSS
│   │   └── main.css         # Main stylesheet
│   ├── js/                  # Compiled JavaScript
│   │   ├── likes.js         # Like system functionality
│   │   ├── main.js          # Core functionality
│   │   └── search.js        # Search functionality
│   └── images/              # Static images
├── themes/                  # Theme directory
│   └── custom-theme/        # Custom theme
│       ├── layouts/         # Theme templates
│       │   ├── _default/    # Default theme templates
│       │   │   ├── baseof.html  # Base template
│       │   │   ├── list.html    # List pages
│       │   │   └── single.html  # Single pages
│       │   └── partials/    # Theme partials
│       │       ├── footer.html  # Footer component
│       │       ├── header.html  # Header component
│       │       └── monetag/     # Monetag ad components
│       └── theme.toml       # Theme configuration
├── public/                  # Generated site (ignored in git)
├── hugo.toml               # Main configuration
└── README.md               # Project documentation
```

## File Naming Conventions
### Content Files
- **Extension**: `.md` for Markdown content
- **Naming**: kebab-case for URLs (e.g., `my-great-post.md`)
- **Location**: Organized by content type in `/content/`

### Template Files
- **Extension**: `.html` for Go templates
- **Naming**: Descriptive names matching Hugo conventions
- **Location**: Theme-specific in `/themes/custom-theme/layouts/`

### JavaScript Files
- **Extension**: `.js` for JavaScript
- **Naming**: Descriptive camelCase (e.g., `searchManager.js`)
- **Location**: `/static/js/` for compiled files

### CSS Files
- **Extension**: `.css` for stylesheets
- **Naming**: Semantic names (e.g., `main.css`, `components.css`)
- **Location**: `/static/css/` for compiled styles

## Hugo Configuration Structure
### Main Configuration (`hugo.toml`)
- **Site Metadata**: Title, description, author, URLs
- **Feature Flags**: Search, likes, Monetag enable/disable
- **SEO Settings**: Meta tags, social media, structured data
- **Output Formats**: HTML, RSS, JSON for search
- **Menu Configuration**: Navigation structure

### Theme Configuration (`theme.toml`)
- **Theme Metadata**: Name, description, version
- **Compatibility**: Hugo version requirements
- **Parameters**: Theme-specific settings

## Content Organization
### Front Matter Standards
```markdown
---
title: "Article Title"
date: 2024-01-15T10:00:00+08:00
draft: false
description: "Brief description for SEO"
keywords: ["keyword1", "keyword2", "keyword3"]
image: "/images/featured-image.jpg"
---
```

### Content Types
1. **Posts**: Blog articles in `/content/posts/`
2. **Pages**: Static pages in `/content/` root
3. **Sections**: Organized content groups
4. **Taxonomies**: Categories and tags automatically generated

## Template Architecture
### Base Template (`baseof.html`)
- HTML skeleton with head and body
- Meta tags and SEO structure
- Script and style includes
- Main content block

### Page Templates
- **Single**: Individual content pages
- **List**: Collections and archive pages
- **Home**: Landing page template
- **Partial**: Reusable components

### Partial Components
- **Header**: Navigation and site header
- **Footer**: Site footer and credits
- **Monetag**: Advertising components
- **Search**: Search interface elements

## JavaScript Architecture
### Module Structure
- **SearchManager**: Handles client-side search functionality
- **LikesManager**: Manages article like system
- **Main**: Core site functionality and event binding

### Storage Patterns
- **localStorage**: User preferences and like data
- **JSON Index**: Search data structure
- **Session Management**: Temporary user state

## CSS Architecture
### Design System
- **CSS Variables**: Consistent theming system
- **Component Styles**: Modular CSS organization
- **Responsive Patterns**: Mobile-first approach
- **Utility Classes**: Reusable styling patterns

### File Organization
- **Main Styles**: `main.css` for global styles
- **Component Styles**: Organized by functionality
- **Theme Variables**: CSS custom properties

## Development Patterns
### New Feature Implementation
1. **Configuration**: Add feature flags to `hugo.toml`
2. **Templates**: Create or modify layout files
3. **JavaScript**: Add functionality to appropriate manager
4. **Styling**: Update CSS with new component styles
5. **Content**: Create documentation and examples

### Content Creation Workflow
1. Use `hugo new posts/filename.md` for new content
2. Follow front matter standards
3. Place images in `/static/images/`
4. Build and test with `hugo server -D`

### Theme Customization
1. Modify `static/css/main.css` for styling
2. Update templates in `themes/custom-theme/layouts/`
3. Add new partials in `themes/custom-theme/layouts/partials/`
4. Create custom shortcodes in `layouts/shortcodes/`

## Build Output Structure
### Generated Site (`/public/`)
- **HTML Pages**: Pre-rendered static pages
- **Assets**: Optimized CSS, JS, and images
- **Search Index**: `index.json` for client-side search
- **Feeds**: RSS and XML sitemaps
- **SEO Files**: robots.txt and meta files

### Deployment Ready
- CDN-optimized file structure
- Proper cache headers
- Minified assets
- SEO-friendly URLs

## Testing Approach
### Manual Testing Areas
1. **Search Functionality**: Test real-time search and results
2. **Like System**: Verify localStorage persistence
3. **Responsive Design**: Test on mobile, tablet, desktop
4. **SEO Markup**: Validate structured data and meta tags
5. **Performance**: Check Lighthouse scores

### Browser Testing
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile devices (iOS, Android)
- Progressive enhancement verification

## Maintenance Guidelines
### Code Quality
- Follow existing patterns and conventions
- Maintain zero external dependencies
- Ensure client-side functionality works without JavaScript
- Keep file sizes within performance budget

### Documentation
- Update README for new features
- Comment complex JavaScript logic
- Maintain consistent front matter patterns
- Document theme customization options