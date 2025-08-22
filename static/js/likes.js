// Article likes functionality
class LikesManager {
    constructor() {
        this.storage = localStorage;
        this.storageKey = 'hugo_article_likes';
        this.userLikesKey = 'hugo_user_likes';
        
        this.init();
    }
    
    init() {
        // Initialize like data if not exists
        if (!this.storage.getItem(this.storageKey)) {
            this.storage.setItem(this.storageKey, JSON.stringify({}));
        }
        
        if (!this.storage.getItem(this.userLikesKey)) {
            this.storage.setItem(this.userLikesKey, JSON.stringify([]));
        }
        
        // Bind events and load initial counts
        this.bindEvents();
        this.loadLikeCounts();
    }
    
    bindEvents() {
        // Bind click events to like buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.like-button')) {
                e.preventDefault();
                const button = e.target.closest('.like-button');
                const postId = button.getAttribute('data-post-id');
                
                if (postId) {
                    this.toggleLike(postId, button);
                }
            }
        });
    }
    
    toggleLike(postId, button) {
        const userLikes = this.getUserLikes();
        const hasLiked = userLikes.includes(postId);
        
        if (hasLiked) {
            // Remove like
            this.removeLike(postId);
            button.classList.remove('liked');
            this.showFeedback(button, 'Like removed');
        } else {
            // Add like
            this.addLike(postId);
            button.classList.add('liked');
            this.showFeedback(button, 'Thank you for liking!');
            
            // Add animation
            button.classList.add('like-animation');
            setTimeout(() => {
                button.classList.remove('like-animation');
            }, 600);
        }
        
        // Update count display
        this.updateLikeCount(postId);
    }
    
    addLike(postId) {
        // Update total likes count
        const likesData = this.getLikesData();
        likesData[postId] = (likesData[postId] || 0) + 1;
        this.storage.setItem(this.storageKey, JSON.stringify(likesData));
        
        // Update user likes
        const userLikes = this.getUserLikes();
        if (!userLikes.includes(postId)) {
            userLikes.push(postId);
            this.storage.setItem(this.userLikesKey, JSON.stringify(userLikes));
        }
    }
    
    removeLike(postId) {
        // Update total likes count
        const likesData = this.getLikesData();
        if (likesData[postId] && likesData[postId] > 0) {
            likesData[postId] -= 1;
            this.storage.setItem(this.storageKey, JSON.stringify(likesData));
        }
        
        // Update user likes
        const userLikes = this.getUserLikes();
        const index = userLikes.indexOf(postId);
        if (index > -1) {
            userLikes.splice(index, 1);
            this.storage.setItem(this.userLikesKey, JSON.stringify(userLikes));
        }
    }
    
    getLikesData() {
        try {
            return JSON.parse(this.storage.getItem(this.storageKey)) || {};
        } catch (e) {
            console.error('Error parsing likes data:', e);
            return {};
        }
    }
    
    getUserLikes() {
        try {
            return JSON.parse(this.storage.getItem(this.userLikesKey)) || [];
        } catch (e) {
            console.error('Error parsing user likes:', e);
            return [];
        }
    }
    
    getLikeCount(postId) {
        const likesData = this.getLikesData();
        return likesData[postId] || 0;
    }
    
    hasUserLiked(postId) {
        const userLikes = this.getUserLikes();
        return userLikes.includes(postId);
    }
    
    updateLikeCount(postId) {
        const count = this.getLikeCount(postId);
        const hasLiked = this.hasUserLiked(postId);
        
        // Update all elements showing this post's like count
        const countElements = document.querySelectorAll(`[data-post-id="${postId}"]`);
        
        countElements.forEach(element => {
            if (element.classList.contains('like-count')) {
                // Direct like count display
                element.textContent = count;
            } else if (element.classList.contains('like-count-display')) {
                // Count display in cards
                element.textContent = count;
            } else if (element.classList.contains('like-button')) {
                // Like button
                const countSpan = element.querySelector('.like-count');
                if (countSpan) {
                    countSpan.textContent = count;
                }
                
                // Update button state
                if (hasLiked) {
                    element.classList.add('liked');
                } else {
                    element.classList.remove('liked');
                }
            }
        });
    }
    
    loadLikeCounts() {
        // Load and display all like counts on page load
        const likeElements = document.querySelectorAll('[data-post-id]');
        const processedIds = new Set();
        
        likeElements.forEach(element => {
            const postId = element.getAttribute('data-post-id');
            if (postId && !processedIds.has(postId)) {
                processedIds.add(postId);
                this.updateLikeCount(postId);
            }
        });
    }
    
    showFeedback(button, message) {
        // Create and show feedback tooltip
        const feedback = document.createElement('div');
        feedback.className = 'like-feedback';
        feedback.textContent = message;
        
        button.appendChild(feedback);
        
        // Position the feedback
        feedback.style.opacity = '1';
        feedback.style.transform = 'translateY(-10px)';
        
        // Remove feedback after animation
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
    }
    
    // API for external usage
    exportData() {
        return {
            likes: this.getLikesData(),
            userLikes: this.getUserLikes()
        };
    }
    
    importData(data) {
        if (data.likes) {
            this.storage.setItem(this.storageKey, JSON.stringify(data.likes));
        }
        if (data.userLikes) {
            this.storage.setItem(this.userLikesKey, JSON.stringify(data.userLikes));
        }
        this.loadLikeCounts();
    }
    
    resetUserLikes() {
        this.storage.setItem(this.userLikesKey, JSON.stringify([]));
        this.loadLikeCounts();
    }
    
    getStats() {
        const likesData = this.getLikesData();
        const userLikes = this.getUserLikes();
        const totalLikes = Object.values(likesData).reduce((sum, count) => sum + count, 0);
        const likedPosts = Object.keys(likesData).length;
        
        return {
            totalLikes,
            likedPosts,
            userLikesCount: userLikes.length,
            averageLikes: likedPosts > 0 ? (totalLikes / likedPosts).toFixed(1) : 0
        };
    }
}

// Initialize likes manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.likesManager = new LikesManager();
    
    // Expose for debugging in console
    if (typeof window !== 'undefined') {
        window.LikesManager = LikesManager;
    }
});