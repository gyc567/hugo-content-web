# Hugo Content Web

A comprehensive Hugo static site framework with advanced features for modern content creators and publishers.

## 🚀 Features

- **🔍 Advanced Search**: Client-side search with real-time results
- **❤️ Like System**: Interactive article likes with local storage
- **📈 SEO Optimized**: Complete SEO setup with structured data
- **💰 Monetag Integration**: Built-in ad monetization support
- **📱 Mobile Responsive**: Optimized for all devices
- **⚡ Performance**: Fast loading with lazy images and optimized assets
- **🎨 Customizable**: Easy to modify themes and layouts

## 🛠️ Quick Start

### Prerequisites

- [Hugo](https://gohugo.io/installation/) v0.100.0 or higher
- [Git](https://git-scm.com/) for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hugo-content-web.git
   cd hugo-content-web
   ```

2. **Start the development server**
   ```bash
   hugo server -D
   ```

3. **Open your browser**
   Navigate to `http://localhost:1313`

### Configuration

Edit `hugo.toml` to customize your site:

```toml
baseURL = "https://your-domain.com"
title = "Your Site Title"

[params]
  description = "Your site description"
  author = "Your Name"
  monetag_site_id = "YOUR_MONETAG_SITE_ID"
  monetag_enabled = true
  search_enabled = true
  likes_enabled = true
```

## 📁 Project Structure

```
hugo-content-web/
├── content/
│   ├── posts/          # Blog posts
│   ├── about.md        # About page
│   └── search.md       # Search page
├── themes/custom-theme/
│   ├── layouts/        # HTML templates
│   └── partials/       # Reusable components
├── static/
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Static images
├── layouts/           # Site-wide layouts
└── hugo.toml         # Configuration file
```

## 🔍 Search Functionality

The search system works entirely client-side using a JSON index:

- **Real-time search** as users type
- **Keyboard shortcut** (Ctrl/Cmd + K) to open search
- **Smart matching** across titles, content, and tags
- **Mobile-optimized** overlay interface

### Customizing Search

Modify search behavior in:
- `layouts/index.json` - Search index structure
- `static/js/search.js` - Search logic and UI

## ❤️ Like System

Interactive like functionality for articles:

- **Local storage** based (no server required)
- **Animated interactions** for better UX
- **Persistent across pages**
- **Export/import** user data

### API Integration

To use server-side storage instead of localStorage:

```javascript
// Configure in static/js/likes.js
window.likesManager.storage = {
    getItem: (key) => fetch(`/api/storage/${key}`),
    setItem: (key, value) => fetch(`/api/storage/${key}`, {
        method: 'POST',
        body: JSON.stringify(value)
    })
};
```

## 💰 Monetag Integration

Built-in support for Monetag advertising:

### Setup

1. Sign up at [Monetag](https://monetag.com)
2. Get your site ID
3. Update configuration:
   ```toml
   [params]
     monetag_enabled = true
     monetag_site_id = "YOUR_SITE_ID"
   ```

### Ad Placements

- **Header/Footer banners** - Automatic placement
- **In-content ads** - Automatic in articles
- **Custom placement** - Use shortcodes

```markdown
{{< monetag-ad type="banner" size="728x90" >}}
Custom ad placement
{{< /monetag-ad >}}
```

### Ad Types Supported

- Banner ads (various sizes)
- Native ads
- Pop-under ads
- In-content ads
- Footer ads

## 📈 SEO Features

Comprehensive SEO optimization:

- **Meta tags** for all pages
- **Open Graph** and **Twitter Cards**
- **Structured data** markup
- **Canonical URLs**
- **Sitemap** generation
- **Robots.txt** support
- **Image optimization**

### SEO Best Practices

```markdown
---
title: "Your Article Title"
description: "Brief description for search engines"
keywords: ["keyword1", "keyword2", "keyword3"]
image: "/images/featured-image.jpg"
---
```

## 🎨 Customization

### Theme Customization

Modify styles in `static/css/main.css`:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    /* Customize colors */
}
```

### Layout Customization

Edit templates in `themes/custom-theme/layouts/`:

- `_default/baseof.html` - Base template
- `_default/single.html` - Article pages
- `_default/list.html` - List pages
- `partials/` - Reusable components

### Adding Features

Create new shortcodes in `layouts/shortcodes/`:

```html
<!-- layouts/shortcodes/custom-component.html -->
<div class="custom-component">
    {{ .Inner | markdownify }}
</div>
```

Usage in content:
```markdown
{{< custom-component >}}
Your content here
{{< /custom-component >}}
```

## 📱 Mobile Optimization

- **Responsive design** for all screen sizes
- **Touch-friendly** navigation
- **Optimized** search interface
- **Fast loading** on mobile connections
- **Accessible** interactions

## ⚡ Performance

- **Static site generation** for fast loading
- **Lazy image loading**
- **Minified assets**
- **Optimized fonts**
- **Efficient search indexing**

### Performance Tips

1. **Optimize images** before uploading
2. **Use WebP format** when possible
3. **Enable CDN** for global delivery
4. **Monitor Core Web Vitals**

## 🚀 Deployment

### Netlify

```toml
# netlify.toml
[build]
  command = "hugo --minify"
  publish = "public"

[context.production.environment]
  HUGO_VERSION = "0.110.0"
  HUGO_ENV = "production"
```

### Vercel

```json
{
  "buildCommand": "hugo --minify",
  "outputDirectory": "public",
  "framework": "hugo"
}
```

### GitHub Pages

```yaml
# .github/workflows/gh-pages.yml
name: GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
      - name: Build
        run: hugo --minify
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

## 📊 Analytics

### Google Analytics

Add to `hugo.toml`:

```toml
[params]
  google_analytics = "G-XXXXXXXXXX"
```

### Custom Tracking

Track user interactions:

```javascript
// Track search usage
gtag('event', 'search', {
  search_term: query
});

// Track likes
gtag('event', 'like', {
  content_id: postId
});
```

## 🔧 Development

### Local Development

```bash
# Start development server
hugo server -D --disableFastRender

# Build for production
hugo --minify

# Clean build cache
hugo --gc
```

### Adding Content

```bash
# Create new post
hugo new posts/my-new-post.md

# Create new page
hugo new about.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines

- Follow existing code style
- Add comments for complex logic
- Test on multiple devices
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join GitHub Discussions for questions
- **Email**: Contact support for urgent issues

## 🗺️ Roadmap

### Upcoming Features

- [ ] Dark mode theme toggle
- [ ] Comment system integration
- [ ] Advanced analytics dashboard
- [ ] Email subscription system
- [ ] Multi-language support
- [ ] E-commerce integration

### Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Enhanced search and like system
- **v1.2.0** - Improved Monetag integration
- **v1.3.0** - Better mobile experience

---

**Ready to start your content journey?** Hugo Content Web provides everything you need to create a professional, fast, and profitable website.

*Star ⭐ this repository if you find it helpful!*



本项目的域名：supercopycoder.xyz