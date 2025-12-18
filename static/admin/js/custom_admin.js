// MusicCityUG Custom Admin JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎵 MusicCityUG Admin loaded');
    
    // Add Spotify-style play button to song cards
    const songCards = document.querySelectorAll('.card');
    songCards.forEach(card => {
        if (card.querySelector('.song-title') || card.querySelector('[data-song]')) {
            const playBtn = document.createElement('button');
            playBtn.className = 'card-play-btn';
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
            playBtn.title = 'Play Preview';
            
            playBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const songId = card.getAttribute('data-song-id') || 
                              card.querySelector('input[type="checkbox"]')?.value;
                if (songId) {
                    playSongPreview(songId);
                }
            });
            
            card.appendChild(playBtn);
        }
    });
    
    // Quick stats update
    updateQuickStats();
    
    // Add music-themed background to login page
    if (document.querySelector('#login-form')) {
        document.body.style.background = 'linear-gradient(135deg, #1e3264 0%, #121212 100%)';
        document.querySelector('.login-box').style.background = 'rgba(255, 255, 255, 0.05)';
        document.querySelector('.login-box').style.backdropFilter = 'blur(10px)';
        document.querySelector('.login-box').style.borderRadius = '16px';
        document.querySelector('.login-box').style.border = '1px solid rgba(255, 255, 255, 0.1)';
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+Shift+S: Quick song add
        if (e.ctrlKey && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            window.location.href = '/admin/music/song/add/';
        }
        
        // Ctrl+Shift+A: Quick artist add
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            e.preventDefault();
            window.location.href = '/admin/artists/artist/add/';
        }
        
        // Ctrl+D: Dashboard
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/admin/';
        }
    });
    
    // Add floating music player for admin previews
    if (window.location.pathname.includes('/admin/music/')) {
        createFloatingPlayer();
    }
});

function playSongPreview(songId) {
    // This would normally make an API call to play the song
    console.log(`🎵 Playing preview for song ID: ${songId}`);
    
    // Show notification
    showNotification('Playing song preview...', 'success');
    
    // In a real implementation, you would:
    // 1. Fetch the song audio URL
    // 2. Play it in the floating player
    // 3. Update play count via API
}

function updateQuickStats() {
    // Fetch and update quick stats from API
    fetch('/api/admin/quick-stats/')
        .then(response => response.json())
        .then(data => {
            // Update stats cards if they exist
            const statsCards = document.querySelectorAll('.stats-card');
            if (statsCards.length) {
                statsCards.forEach(card => {
                    const statType = card.getAttribute('data-stat');
                    if (statType && data[statType]) {
                        const numberEl = card.querySelector('.stats-number');
                        if (numberEl) {
                            numberEl.textContent = data[statType];
                        }
                    }
                });
            }
        })
        .catch(error => console.error('Error fetching stats:', error));
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--spotify-card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid ${type === 'success' ? 'var(--spotify-green)' : 
                               type === 'error' ? '#FF4747' : 
                               type === 'warning' ? '#FFD700' : '#1E90FF'};
        border-radius: 12px;
        padding: 15px 20px;
        color: var(--spotify-text-primary);
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
        box-shadow: var(--spotify-shadow);
    `;
    
    document.body.appendChild(notification);
    
    // Add close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function createFloatingPlayer() {
    const player = document.createElement('div');
    player.id = 'floating-music-player';
    player.innerHTML = `
        <div class="player-header">
            <span>🎵 Now Playing</span>
            <button class="player-close"><i class="fas fa-times"></i></button>
        </div>
        <div class="player-body">
            <div class="player-info">
                <div class="player-artwork">🎵</div>
                <div class="player-details">
                    <div class="player-title">No song selected</div>
                    <div class="player-artist">Select a song to play</div>
                </div>
            </div>
            <div class="player-controls">
                <button class="player-btn prev"><i class="fas fa-step-backward"></i></button>
                <button class="player-btn play-pause"><i class="fas fa-play"></i></button>
                <button class="player-btn next"><i class="fas fa-step-forward"></i></button>
            </div>
            <div class="player-progress">
                <div class="progress-bar">
                    <div class="progress-fill"></div>
                </div>
                <div class="player-time">0:00 / 0:00</div>
            </div>
        </div>
    `;
    
    player.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        background: var(--spotify-card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: var(--spotify-shadow);
        z-index: 1000;
        overflow: hidden;
    `;
    
    document.body.appendChild(player);
    
    // Add player styles
    const playerStyles = document.createElement('style');
    playerStyles.textContent = `
        #floating-music-player .player-header {
            background: var(--spotify-light-gray);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        #floating-music-player .player-header span {
            color: var(--spotify-text-primary);
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        #floating-music-player .player-close {
            background: transparent;
            border: none;
            color: var(--spotify-text-secondary);
            cursor: pointer;
            font-size: 0.9rem;
        }
        
        #floating-music-player .player-body {
            padding: 20px;
        }
        
        #floating-music-player .player-info {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        #floating-music-player .player-artwork {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--spotify-green), #1ed760);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        #floating-music-player .player-title {
            color: var(--spotify-text-primary);
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        #floating-music-player .player-artist {
            color: var(--spotify-text-secondary);
            font-size: 0.9rem;
        }
        
        #floating-music-player .player-controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 15px;
        }
        
        #floating-music-player .player-btn {
            background: var(--spotify-green);
            color: var(--spotify-black);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        #floating-music-player .player-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(29, 185, 84, 0.3);
        }
        
        #floating-music-player .player-progress {
            margin-top: 10px;
        }
        
        #floating-music-player .progress-bar {
            height: 4px;
            background: var(--spotify-lighter-gray);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        #floating-music-player .progress-fill {
            height: 100%;
            background: var(--spotify-green);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        #floating-music-player .player-time {
            display: flex;
            justify-content: space-between;
            color: var(--spotify-text-secondary);
            font-size: 0.8rem;
        }
    `;
    
    document.head.appendChild(playerStyles);
    
    // Close button functionality
    player.querySelector('.player-close').addEventListener('click', () => {
        player.style.transform = 'translateY(100px)';
        player.style.opacity = '0';
        setTimeout(() => player.remove(), 300);
    });
}

// Add CSS animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(animationStyles);
