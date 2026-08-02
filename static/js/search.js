// Global search functionality
class SearchManager {
    constructor() {
        this.searchIndex = null;
        this.searchOverlay = document.getElementById('search-overlay');
        this.searchInput = document.getElementById('search-input');
        this.searchResults = document.getElementById('search-results');
        this.searchToggle = document.getElementById('search-toggle');
        this.searchClose = document.getElementById('search-close');
        
        this.init();
    }
    
    async init() {
        try {
            // Load search index
            const response = await fetch('/index.json');
            this.searchIndex = await response.json();
            
            // Bind events
            this.bindEvents();
        } catch (error) {
            console.error('Failed to load search index:', error);
        }
    }
    
    bindEvents() {
        if (this.searchToggle) {
            this.searchToggle.addEventListener('click', () => this.openSearch());
        }
        
        if (this.searchClose) {
            this.searchClose.addEventListener('click', () => this.closeSearch());
        }
        
        if (this.searchOverlay) {
            this.searchOverlay.addEventListener('click', (e) => {
                if (e.target === this.searchOverlay) {
                    this.closeSearch();
                }
            });
        }
        
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.performSearch(e.target.value));
            this.searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeSearch();
                }
            });
        }
        
        // Global keyboard shortcut (Ctrl+K or Cmd+K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openSearch();
            }
        });
    }
    
    openSearch() {
        if (this.searchOverlay) {
            this.searchOverlay.classList.add('active');
            if (this.searchInput) {
                this.searchInput.focus();
            }
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeSearch() {
        if (this.searchOverlay) {
            this.searchOverlay.classList.remove('active');
            if (this.searchInput) {
                this.searchInput.value = '';
            }
            if (this.searchResults) {
                this.searchResults.innerHTML = '';
            }
            document.body.style.overflow = '';
        }
    }
    
    performSearch(query) {
        if (!this.searchResults || !this.searchIndex) return;
        
        const trimmedQuery = query.trim().toLowerCase();
        
        if (!trimmedQuery) {
            this.searchResults.innerHTML = '';
            return;
        }
        
        if (trimmedQuery.length < 2) {
            this.searchResults.innerHTML = '<div class="search-message">Type at least 2 characters to search...</div>';
            return;
        }
        
        // 阶段1: 基础关键词匹配
        let results = this.searchIndex.filter(item => {
            return item.title.toLowerCase().includes(trimmedQuery) ||
                   item.content.toLowerCase().includes(trimmedQuery) ||
                   (item.tags && item.tags.some(tag => tag.toLowerCase().includes(trimmedQuery)));
        });
        
        // 阶段2: 相似文章去重 - 同系列文章只保留最新
        results = this.deduplicateSimilarArticles(results);
        
        // 阶段3: 限制结果数量
        results = results.slice(0, 10);
        
        this.displayResults(results, trimmedQuery);
    }
    
    /**
     * 相似文章去重
     * 策略：同系列文章（如 github-claude-prompts-review-2026-07-27 和 
     *       github-claude-prompts-review-2026-08-01）只保留最新的一篇
     */
    deduplicateSimilarArticles(results) {
        if (results.length <= 1) return results;
        
        // 按日期倒序排序（最新的在前）
        results.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        const seen = new Set();
        
        return results.filter(item => {
            // 提取文章基础slug（去掉日期部分）
            // 例如: github-claude-prompts-review-2026-07-27 -> github-claude-prompts-review
            const slug = this.extractArticleSlug(item.url);
            
            if (seen.has(slug)) {
                return false; // 同系列文章，已有过更新的，跳过
            }
            seen.add(slug);
            return true;
        });
    }
    
    /**
     * 从URL中提取文章基础slug
     * 例如: /posts/github-claude-prompts-review-2026-07-27 -> github-claude-prompts-review
     */
    extractArticleSlug(url) {
        if (!url) return '';
        
        // 获取URL最后一部分（文件名）
        const parts = url.split('/');
        const filename = parts[parts.length - 1];
        
        // 去掉 .html 或 .md 扩展名
        const nameWithoutExt = filename.replace(/\.(html|md)$/, '');
        
        // 去掉日期后缀 (YYYY-MM-DD 或 YYYYMMDD)
        // 匹配末尾的日期模式
        const slugWithoutDate = nameWithoutExt.replace(/[-_]?\d{4}[-_]\d{2}[-_]\d{2}$/, '');
        
        // 进一步规范化：去掉末尾的分隔符
        return slugWithoutDate.replace(/[-_]$/, '');
    }
    
    displayResults(results, query) {
        if (results.length === 0) {
            this.searchResults.innerHTML = `
                <div class="search-message">
                    <p>No results found for "${query}"</p>
                </div>
            `;
            return;
        }
        
        const resultsHtml = results.map(item => {
            const highlightedTitle = this.highlightText(item.title, query);
            const highlightedExcerpt = this.highlightText(item.content.substring(0, 150) + '...', query);
            
            return `
                <div class="search-result-item">
                    <h4 class="search-result-title">
                        <a href="${item.url}" onclick="searchManager.closeSearch()">${highlightedTitle}</a>
                    </h4>
                    <p class="search-result-excerpt">${highlightedExcerpt}</p>
                    <div class="search-result-meta">
                        <span class="search-result-date">${item.date}</span>
                        ${item.tags ? `<div class="search-result-tags">${item.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        this.searchResults.innerHTML = `
            <div class="search-results-header">
                <p>Found ${results.length} result${results.length !== 1 ? 's' : ''} for "${query}"</p>
            </div>
            ${resultsHtml}
        `;
    }
    
    highlightText(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${this.escapeRegExp(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.searchManager = new SearchManager();
});