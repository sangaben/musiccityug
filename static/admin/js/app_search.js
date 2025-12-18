// App-Specific Search Functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 MusicCityUG App-Specific Search Loaded');
    
    // Define app search configurations
    const appSearchConfigs = {
        'music': {
            endpoint: '/api/admin/music/search/',
            placeholder: 'Search songs, albums, genres...',
            models: ['Song', 'Album', 'Genre']
        },
        'artists': {
            endpoint: '/api/admin/artists/search/',
            placeholder: 'Search artists, bands...',
            models: ['Artist', 'Band']
        },
        'accounts': {
            endpoint: '/api/admin/accounts/search/',
            placeholder: 'Search users, profiles...',
            models: ['User', 'UserProfile']
        },
        'payments': {
            endpoint: '/api/admin/payments/search/',
            placeholder: 'Search transactions, subscriptions...',
            models: ['Transaction', 'Subscription']
        },
        'analytics': {
            endpoint: '/api/admin/analytics/search/',
            placeholder: 'Search plays, downloads, analytics...',
            models: ['PlayAnalytic', 'DownloadAnalytic']
        },
        'library': {
            endpoint: '/api/admin/library/search/',
            placeholder: 'Search collections, playlists...',
            models: ['Collection']
        },
        'news': {
            endpoint: '/api/admin/news/search/',
            placeholder: 'Search articles, categories...',
            models: ['Article', 'Category']
        },
        'help': {
            endpoint: '/api/admin/help/search/',
            placeholder: 'Search FAQs, support tickets...',
            models: ['FAQ', 'SupportTicket']
        }
    };
    
    // Initialize app search functionality
    initializeAppSearch();
    
    function initializeAppSearch() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        
        // Add search functionality to each app in sidebar
        const navItems = sidebar.querySelectorAll('.nav-sidebar .nav-item');
        
        navItems.forEach(navItem => {
            const navLink = navItem.querySelector('.nav-link');
            if (!navLink) return;
            
            // Find app name from link
            const linkHref = navLink.getAttribute('href') || '';
            const appName = extractAppName(linkHref);
            
            if (appName && appSearchConfigs[appName]) {
                // Add search class and functionality
                navItem.classList.add('has-search');
                
                // Add click event for search toggle
                navLink.addEventListener('click', function(e) {
                    // If it's not the actual model link (has children), toggle search
                    if (navItem.querySelector('.nav-treeview')) {
                        e.preventDefault();
                        e.stopPropagation();
                        toggleAppSearch(appName, navItem);
                    }
                });
            }
        });
        
        // Add global keyboard shortcut (Ctrl+/)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                const activeApp = getActiveApp();
                if (activeApp) {
                    const navItem = document.querySelector(`[data-app="${activeApp}"]`);
                    if (navItem) {
                        toggleAppSearch(activeApp, navItem);
                        // Focus the search input
                        const searchInput = navItem.querySelector('.app-search-input');
                        if (searchInput) {
                            searchInput.focus();
                        }
                    }
                }
            }
            
            // Escape to close all searches
            if (e.key === 'Escape') {
                closeAllAppSearches();
            }
        });
    }
    
    function extractAppName(href) {
        // Extract app name from URL
        if (!href) return null;
        
        // Match patterns like /admin/music/, /admin/artists/, etc.
        const match = href.match(/\/admin\/([^\/]+)\//);
        if (match && match[1]) {
            return match[1];
        }
        return null;
    }
    
    function toggleAppSearch(appName, navItem) {
        // Check if search is already active
        const isActive = navItem.classList.contains('search-active');
        
        // Close all other searches first
        closeAllAppSearches();
        
        if (!isActive) {
            // Create and show search container
            const searchContainer = createSearchContainer(appName);
            navItem.appendChild(searchContainer);
            navItem.classList.add('search-active');
            
            // Focus input after animation
            setTimeout(() => {
                const input = searchContainer.querySelector('.app-search-input');
                if (input) input.focus();
            }, 300);
        }
    }
    
    function createSearchContainer(appName) {
        const config = appSearchConfigs[appName];
        
        const container = document.createElement('div');
        container.className = 'app-search-container active';
        container.innerHTML = `
            <div class="app-search-header">
                <h6>Search ${appName.charAt(0).toUpperCase() + appName.slice(1)}</h6>
                <button class="app-search-close" title="Close search">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <input type="text" 
                   class="app-search-input" 
                   placeholder="${config.placeholder}"
                   autocomplete="off">
            <div class="app-search-results"></div>
        `;
        
        // Add close functionality
        container.querySelector('.app-search-close').addEventListener('click', function(e) {
            e.stopPropagation();
            closeAppSearch(container);
        });
        
        // Add search functionality
        const searchInput = container.querySelector('.app-search-input');
        const resultsContainer = container.querySelector('.app-search-results');
        
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(appName, query, resultsContainer);
                }, 300);
            } else {
                clearResults(resultsContainer);
            }
        });
        
        // Prevent click propagation
        container.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        return container;
    }
    
    async function performSearch(appName, query, resultsContainer) {
        const config = appSearchConfigs[appName];
        
        try {
            // Show loading
            resultsContainer.innerHTML = '<div class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
            
            // In a real implementation, you would make an API call here
            // For now, we'll simulate with mock data
            const mockResults = getMockResults(appName, query);
            
            // Display results
            displayResults(mockResults, resultsContainer, appName);
            
        } catch (error) {
            console.error('Search error:', error);
            resultsContainer.innerHTML = '<div class="app-search-no-results">Search error occurred</div>';
        }
    }
    
    function getMockResults(appName, query) {
        // Mock data for demonstration
        const mockData = {
            'music': [
                { id: 1, name: `Song: "${query}" - Artist 1`, url: '/admin/music/song/1/change/', icon: 'fas fa-music', type: 'Song' },
                { id: 2, name: `Album: "${query} Hits"`, url: '/admin/music/album/2/change/', icon: 'fas fa-compact-disc', type: 'Album' },
                { id: 3, name: `Genre: ${query}`, url: '/admin/music/genre/3/change/', icon: 'fas fa-tag', type: 'Genre' }
            ],
            'artists': [
                { id: 1, name: `Artist: ${query}`, url: '/admin/artists/artist/1/change/', icon: 'fas fa-user-tie', type: 'Artist' },
                { id: 2, name: `Band: ${query} Crew`, url: '/admin/artists/band/2/change/', icon: 'fas fa-users', type: 'Band' }
            ],
            'accounts': [
                { id: 1, name: `User: ${query}`, url: '/admin/auth/user/1/change/', icon: 'fas fa-user', type: 'User' },
                { id: 2, name: `Profile: ${query}'s Profile`, url: '/admin/accounts/userprofile/2/change/', icon: 'fas fa-id-card', type: 'Profile' }
            ]
        };
        
        return mockData[appName] || [{ id: 1, name: `No results found for "${query}"`, url: '#', icon: 'fas fa-search', type: 'Info' }];
    }
    
    function displayResults(results, container, appName) {
        if (results.length === 0) {
            container.innerHTML = '<div class="app-search-no-results">No results found</div>';
            return;
        }
        
        let html = '';
        results.forEach(result => {
            html += `
                <a href="${result.url}" class="app-search-result-item">
                    <i class="${result.icon}"></i>
                    <span>${result.name}</span>
                    <small style="float: right; opacity: 0.7;">${result.type}</small>
                </a>
            `;
        });
        
        // Add quick actions
        html += `
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                <a href="/admin/${appName}/" class="app-search-result-item">
                    <i class="fas fa-list"></i>
                    <span>View all ${appName}</span>
                </a>
                <a href="/admin/${appName}/add/" class="app-search-result-item">
                    <i class="fas fa-plus"></i>
                    <span>Add new</span>
                </a>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    function clearResults(container) {
        container.innerHTML = '';
    }
    
    function closeAppSearch(searchContainer) {
        const navItem = searchContainer.closest('.nav-item');
        if (navItem) {
            navItem.classList.remove('search-active');
            searchContainer.classList.remove('active');
            setTimeout(() => {
                if (searchContainer.parentNode) {
                    searchContainer.remove();
                }
            }, 300);
        }
    }
    
    function closeAllAppSearches() {
        document.querySelectorAll('.app-search-container').forEach(container => {
            closeAppSearch(container);
        });
        document.querySelectorAll('.nav-item.search-active').forEach(item => {
            item.classList.remove('search-active');
        });
    }
    
    function getActiveApp() {
        // Determine which app is currently active based on URL
        const path = window.location.pathname;
        const match = path.match(/\/admin\/([^\/]+)/);
        return match ? match[1] : null;
    }
    
    // Add app data attributes for easier selection
    document.querySelectorAll('.nav-sidebar .nav-item').forEach(item => {
        const link = item.querySelector('.nav-link');
        if (link) {
            const appName = extractAppName(link.getAttribute('href'));
            if (appName) {
                item.setAttribute('data-app', appName);
            }
        }
    });
});
