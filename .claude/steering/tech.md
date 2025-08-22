# Technology Stack - Hugo Content Web

## Core Framework
- **Hugo**: v0.100.0+ (Go-based static site generator)
- **Go Templates**: Hugo's templating language for dynamic content
- **Markdown**: Content creation format with front matter support

## Frontend Technologies
### JavaScript
- **Vanilla ES6+**: No external frameworks or dependencies
- **Modern Features**: Classes, async/await, modules, localStorage
- **Architecture**: Modular class-based structure (SearchManager, LikesManager)

### CSS & Styling
- **Custom CSS**: No CSS frameworks (Bootstrap, Tailwind, etc.)
- **CSS Variables**: Custom properties for theming and consistency
- **Responsive Design**: Mobile-first approach with media queries
- **Modern Features**: Flexbox, Grid, CSS transitions/animations

### Key JavaScript Components
1. **SearchManager** (`search.js`): Client-side search with JSON index
2. **LikesManager** (`likes.js`): Article like system with localStorage
3. **Main** (`main.js`): Core functionality and mobile navigation

## Third-Party Integrations
### Advertising
- **Monetag**: Primary ad monetization platform
- **Integration**: Script injection via Hugo partials
- **Configuration**: Site ID and enable/disable via `hugo.toml`

### Analytics (Optional)
- **Google Analytics**: Support for GA4 measurement ID
- **Custom Tracking**: Event tracking for search and likes

## Build & Deployment
### Development Commands
```bash
# Start development server
hugo server -D
hugo server -D --disableFastRender  # For better development experience

# Production build
hugo --minify  # Minified output with optimized assets

# Clean build cache
hugo --gc
```

### Deployment Targets
- **Netlify**: Built-in Hugo support with `netlify.toml`
- **Vercel**: Framework configuration with `vercel.json`
- **GitHub Pages**: GitHub Actions workflow support
- **Any Static Host**: CDN-compatible output

## Performance Requirements
### Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

### Optimization Strategies
- **Static Generation**: Pre-built HTML pages
- **Lazy Loading**: Images loaded on demand
- **Asset Optimization**: Minified CSS/JS, optimized images
- **CDN Ready**: Proper cache headers and asset versioning

## Browser Compatibility
### Supported Browsers
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions
- **Mobile**: iOS Safari, Chrome Mobile

### JavaScript Features Used
- ES6 Modules (import/export)
- Async/Await
- Classes
- Arrow functions
- Template literals
- Destructuring
- localStorage API
- Fetch API
- DOM manipulation

## Technical Constraints
### Must Maintain
- **Zero External Dependencies**: No npm packages or CDN resources
- **Client-Side Only**: No server-side processing requirements
- **Static Output**: All functionality must work with pre-built HTML
- **Progressive Enhancement**: Core content accessible without JavaScript

### Performance Budget
- **Total JS**: < 100KB (minified)
- **Total CSS**: < 50KB (minified)
- **Page Weight**: < 500KB total (excluding images)
- **HTTP Requests**: < 15 per page

## Development Tools
### Required Software
- **Hugo**: v0.100.0 or higher
- **Git**: Version control
- **Text Editor**: VS Code, Sublime Text, etc.

### Recommended Tools
- **Browser DevTools**: For debugging and performance analysis
- **Lighthouse**: For performance and SEO auditing
- **WebPageTest**: For comprehensive performance testing

## Security Considerations
- **Content Security Policy**: Ready for CSP implementation
- **XSS Protection**: Proper input sanitization in search
- **LocalStorage**: Secure data handling for user preferences
- **Third-Party Scripts**: Careful evaluation of external services

## Monitoring & Analytics
### Built-in Tracking
- Search usage statistics
- Like interaction tracking
- Page performance metrics

### Integration Points
- Google Analytics (optional)
- Custom event tracking hooks
- Performance monitoring ready