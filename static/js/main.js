// Enhanced Player functionality
let currentSong = null;
let isPlaying = false;
let currentPlaylist = [];
let currentSongIndex = -1;
let isShuffled = false;
let isRepeating = false;
let originalPlaylist = [];

const audioPlayer = document.getElementById('audio-player');
const playerSection = document.getElementById('player-section');
const playPauseBtn = document.getElementById('play-pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const repeatBtn = document.getElementById('repeat-btn');
const progressBar = document.getElementById('progress-bar');
const progress = document.getElementById('progress');
const currentTimeEl = document.getElementById('current-time');
const durationEl = document.getElementById('duration');
const currentSongTitle = document.getElementById('current-song-title');
const currentSongArtist = document.getElementById('current-song-artist');
const currentSongThumb = document.getElementById('current-song-thumb');

// Initialize player
document.addEventListener('DOMContentLoaded', function() {
    if (audioPlayer) {
        audioPlayer.volume = 0.7;
        updateVolumeDisplay();
        
        // Auto-play next song when current ends
        audioPlayer.addEventListener('ended', function() {
            if (currentPlaylist.length > 0) {
                playNextSong();
            } else {
                // If no playlist, just stop
                pauseAudio();
            }
        });
    }
});

// Format time function
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// Update progress bar
function updateProgress() {
    if (audioPlayer && audioPlayer.duration) {
        const progressPercent = (audioPlayer.currentTime / audioPlayer.duration) * 100;
        progress.style.width = `${progressPercent}%`;
        currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
    }
}

// Update volume display
function updateVolumeDisplay() {
    const volumeLevel = document.getElementById('volume-level');
    if (volumeLevel && audioPlayer) {
        volumeLevel.style.width = `${audioPlayer.volume * 100}%`;
    }
}

// Play song function - UPDATED with play tracking
function playSong(songData, playlist = [], index = 0) {
    if (!audioPlayer) return;
    
    if (playlist && playlist.length > 0) {
        currentPlaylist = playlist;
        currentSongIndex = index;
        originalPlaylist = [...playlist];
    }
    
    currentSong = songData;
    
    // Show player section
    if (playerSection) {
        playerSection.classList.add('active');
    }
    
    // Update UI
    if (currentSongThumb) {
        currentSongThumb.style.backgroundImage = `url('${songData.cover || '/static/images/default-cover.jpg'}')`;
    }
    if (currentSongTitle) {
        currentSongTitle.textContent = songData.title;
    }
    if (currentSongArtist) {
        currentSongArtist.textContent = songData.artist;
    }
    
    // Set audio source and play
    audioPlayer.src = songData.audio;
    audioPlayer.load();
    
    // Update duration when metadata is loaded
    audioPlayer.addEventListener('loadedmetadata', function() {
        if (durationEl) {
            durationEl.textContent = formatTime(audioPlayer.duration);
        }
    });
    
    // Track the play when song starts
    audioPlayer.addEventListener('play', function onPlay() {
        // Remove this listener to avoid duplicate tracking
        audioPlayer.removeEventListener('play', onPlay);
        
        // Track the play via Django endpoint
        if (songData.id) {
            trackSongPlay(songData.id);
            triggerSongPlayed(songData.id);
        }
    });
    
    playAudio();
}

function playAudio() {
    if (!audioPlayer) return;
    
    audioPlayer.play()
        .then(() => {
            isPlaying = true;
            if (playPauseBtn) {
                playPauseBtn.querySelector('i').classList.remove('fa-play');
                playPauseBtn.querySelector('i').classList.add('fa-pause');
            }
        })
        .catch(error => {
            console.error('Error playing audio:', error);
        });
}

function pauseAudio() {
    if (!audioPlayer) return;
    
    audioPlayer.pause();
    isPlaying = false;
    if (playPauseBtn) {
        playPauseBtn.querySelector('i').classList.remove('fa-pause');
        playPauseBtn.querySelector('i').classList.add('fa-play');
    }
}

function togglePlayPause() {
    if (!currentSong || !audioPlayer) return;
    
    if (isPlaying) {
        pauseAudio();
    } else {
        playAudio();
    }
}

function playNextSong() {
    if (currentPlaylist.length === 0) return;
    
    if (isRepeating) {
        // If repeating, play current song again
        if (audioPlayer) {
            audioPlayer.currentTime = 0;
            playAudio();
        }
        return;
    }
    
    if (currentSongIndex < currentPlaylist.length - 1) {
        currentSongIndex++;
    } else {
        // End of playlist - loop to beginning
        currentSongIndex = 0;
    }
    
    const nextSong = currentPlaylist[currentSongIndex];
    playSong(nextSong, currentPlaylist, currentSongIndex);
}

function playPrevSong() {
    if (currentPlaylist.length === 0) return;
    
    if (audioPlayer && audioPlayer.currentTime > 3) {
        // If more than 3 seconds into song, restart current song
        audioPlayer.currentTime = 0;
        playAudio();
        return;
    }
    
    if (currentSongIndex > 0) {
        currentSongIndex--;
    } else {
        currentSongIndex = currentPlaylist.length - 1;
    }
    
    const prevSong = currentPlaylist[currentSongIndex];
    playSong(prevSong, currentPlaylist, currentSongIndex);
}

function toggleShuffle() {
    isShuffled = !isShuffled;
    if (shuffleBtn) {
        shuffleBtn.style.color = isShuffled ? 'var(--primary)' : 'var(--gray)';
    }
    
    if (isShuffled && currentPlaylist.length > 0) {
        // Create shuffled playlist
        const shuffled = [...originalPlaylist];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        currentPlaylist = shuffled;
        // Find current song in shuffled playlist
        if (currentSong) {
            currentSongIndex = currentPlaylist.findIndex(song => song.id === currentSong.id);
        }
    } else if (!isShuffled && originalPlaylist.length > 0) {
        // Restore original order
        currentPlaylist = [...originalPlaylist];
        if (currentSong) {
            currentSongIndex = currentPlaylist.findIndex(song => song.id === currentSong.id);
        }
    }
}

function toggleRepeat() {
    isRepeating = !isRepeating;
    if (repeatBtn) {
        repeatBtn.style.color = isRepeating ? 'var(--primary)' : 'var(--gray)';
    }
}

// ========== PLAY COUNTING FUNCTIONS ==========

// Track song play in the database
function trackSongPlay(songId) {
    fetch(`/play-song/${songId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => {
        if (response.status === 401) {
            // User is not authenticated, use anonymous endpoint
            return fetch(`/api/track-anonymous-play/${songId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            });
        }
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        return response;
    })
    .then(response => response.json())
    .then(data => {
        if (data.error && data.error.includes('Premium')) {
            console.log('Premium content restriction:', data.error);
            return;
        }
        
        if (data.success || data.plays !== undefined) {
            console.log('Play tracked successfully:', data);
        }
    })
    .catch(error => {
        console.error('Error tracking play:', error);
    });
}

// Trigger custom event for other page components
function triggerSongPlayed(songId) {
    const event = new CustomEvent('songPlayed', { detail: { songId } });
    document.dispatchEvent(event);
}

// ========== ENHANCED DOWNLOAD FUNCTION ==========
function downloadSong(songUrl, songTitle, artistName, songId = null) {
    if (songId) {
        // If we have a song ID, use the proper download endpoint
        window.open(`/download-song/${songId}/`, '_blank');
        
        // Trigger download event
        triggerSongDownloaded(songId);
    } else {
        // Fallback to direct download
        const link = document.createElement('a');
        link.href = songUrl;
        link.download = `${songTitle} - ${artistName}.mp3`;
        console.log(`Downloading: ${songTitle} by ${artistName}`);
        link.click();
    }
    
    // Track download analytics
    trackDownload(songTitle, artistName, songId);
}

// Trigger custom event for download
function triggerSongDownloaded(songId) {
    const event = new CustomEvent('songDownloaded', { detail: { songId } });
    document.dispatchEvent(event);
}

function trackDownload(songTitle, artistName, songId = null) {
    // Send analytics data to your backend
    console.log(`Download tracked: ${songTitle} by ${artistName}`);
    
    // You can send this data to your analytics service
    fetch('/api/track-download/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            song_id: songId,
            song_title: songTitle,
            artist_name: artistName,
            timestamp: new Date().toISOString()
        })
    }).catch(error => {
        console.error('Error tracking download:', error);
    });
}

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to play a single song
function playThisSong(songId) {
    // Get song data from your data structure or API
    const songData = getSongDataById(songId);
    
    if (songData) {
        // Create a playlist with just this song for auto-play continuity
        const playlist = [songData];
        playSong(songData, playlist, 0);
    }
}

// Example function to get song data (implement based on your data structure)
function getSongDataById(songId) {
    // This should return song data from your page or make an API call
    // Example structure:
    const songElement = document.querySelector(`[data-song-id="${songId}"]`);
    if (songElement) {
        return {
            id: songId,
            title: songElement.querySelector('.song-title')?.textContent || 'Unknown Title',
            artist: songElement.querySelector('.song-artist')?.textContent || 'Unknown Artist',
            audio: songElement.dataset.audioUrl || '#',
            cover: songElement.dataset.coverUrl || '/static/images/default-cover.jpg'
        };
    }
    
    // Try to find in window playlists
    if (window.homePlaylist) {
        const song = window.homePlaylist.find(s => s.id === songId);
        if (song) return song;
    }
    
    if (window.discoverPlaylist) {
        const song = window.discoverPlaylist.find(s => s.id === songId);
        if (song) return song;
    }
    
    return null;
}

// Event listeners for player controls
if (playPauseBtn) {
    playPauseBtn.addEventListener('click', togglePlayPause);
}
if (prevBtn) {
    prevBtn.addEventListener('click', playPrevSong);
}
if (nextBtn) {
    nextBtn.addEventListener('click', playNextSong);
}
if (shuffleBtn) {
    shuffleBtn.addEventListener('click', toggleShuffle);
}
if (repeatBtn) {
    repeatBtn.addEventListener('click', toggleRepeat);
}

// Progress bar click to seek
if (progressBar) {
    progressBar.addEventListener('click', function(e) {
        if (!audioPlayer || !audioPlayer.duration) return;
        
        const rect = progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        audioPlayer.currentTime = percent * audioPlayer.duration;
    });
}

// Volume control
const volumeBar = document.getElementById('volume-bar');
if (volumeBar) {
    volumeBar.addEventListener('click', function(e) {
        if (!audioPlayer) return;
        
        const rect = volumeBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        audioPlayer.volume = Math.max(0, Math.min(1, percent));
        updateVolumeDisplay();
    });
}

// Audio player event listeners
if (audioPlayer) {
    audioPlayer.addEventListener('timeupdate', updateProgress);
}

// Enhanced contact functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add click tracking for contact methods
    const contactLinks = document.querySelectorAll('.contact-item, .contact-link');
    
    contactLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const contactType = this.classList.contains('whatsapp') ? 'whatsapp' : 'email';
            console.log(`Contact initiated via ${contactType}`);
        });
    });

    // Add download button event listeners
    const downloadButtons = document.querySelectorAll('.download-btn');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const songId = this.dataset.songId;
            const songUrl = this.dataset.songUrl;
            const songTitle = this.dataset.songTitle;
            const artistName = this.dataset.artistName;
            
            if (songId) {
                // Use the enhanced download function with tracking
                downloadSong(songUrl, songTitle, artistName, songId);
            } else if (songUrl && songTitle && artistName) {
                // Fallback to direct download
                downloadSong(songUrl, songTitle, artistName);
            }
        });
    });
});

// Function to open WhatsApp with custom message
function openWhatsApp(message = "Hello MusicCity UG Team, I need help uploading my music") {
    const phoneNumber = "256766670007";
    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/${phoneNumber}?text=${encodedMessage}`, '_blank');
}

// Function to open email with custom subject and body
function openEmail(subject = "Music Upload Support - MusicCity UG", body = "Hello MusicCity UG Team,\n\nI need assistance with uploading my music.\n\nThank you.") {
    const email = "musiccityug@gmail.com";
    const encodedSubject = encodeURIComponent(subject);
    const encodedBody = encodeURIComponent(body);
    window.location.href = `mailto:${email}?subject=${encodedSubject}&body=${encodedBody}`;
}

// Close watermark function
function closeWatermark() {
    const watermark = document.getElementById('watermark-overlay');
    if (watermark) {
        watermark.style.display = 'none';
    }
}

// Modal functionality
const loginModal = document.getElementById('login-modal');
const signupModal = document.getElementById('signup-modal');
const loginCancel = document.getElementById('login-cancel');
const signupCancel = document.getElementById('signup-cancel');

if (loginCancel) {
    loginCancel.addEventListener('click', function() {
        if (loginModal) loginModal.style.display = 'none';
    });
}

if (signupCancel) {
    signupCancel.addEventListener('click', function() {
        if (signupModal) signupModal.style.display = 'none';
    });
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    if (loginModal && event.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (signupModal && event.target === signupModal) {
        signupModal.style.display = 'none';
    }
});

// Make functions globally available
window.playSong = playSong;
window.playThisSong = playThisSong;
window.togglePlayPause = togglePlayPause;
window.currentPlaylist = currentPlaylist;
window.downloadSong = downloadSong;
window.openWhatsApp = openWhatsApp;
window.openEmail = openEmail;
window.trackSongPlay = trackSongPlay;
window.triggerSongPlayed = triggerSongPlayed;
window.triggerSongDownloaded = triggerSongDownloaded;
window.getCookie = getCookie;