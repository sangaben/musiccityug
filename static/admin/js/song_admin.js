// Song Admin Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // File upload drag and drop
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const parent = input.closest('.form-row') || input.closest('.fieldBox');
        if (parent) {
            const uploadArea = document.createElement('div');
            uploadArea.className = 'upload-box';
            
            const icon = document.createElement('i');
            icon.className = 'fas fa-cloud-upload-alt upload-icon';
            
            const title = document.createElement('h3');
            title.textContent = 'Click to upload or drag & drop';
            
            const description = document.createElement('p');
            description.textContent = input.getAttribute('data-help') || 'Upload your file here';
            
            const currentFile = document.createElement('div');
            currentFile.className = 'current-file';
            
            // Move input inside upload area
            uploadArea.appendChild(icon);
            uploadArea.appendChild(title);
            uploadArea.appendChild(description);
            uploadArea.appendChild(input.cloneNode(true));
            uploadArea.appendChild(currentFile);
            
            // Replace original input
            input.parentNode.replaceChild(uploadArea, input);
            
            // Style the new input
            const newInput = uploadArea.querySelector('input[type="file"]');
            newInput.style.display = 'none';
            
            // Click on upload area to trigger file input
            uploadArea.addEventListener('click', function(e) {
                if (e.target !== newInput) {
                    newInput.click();
                }
            });
            
            // Drag and drop events
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('drag-over');
            });
            
            uploadArea.addEventListener('dragleave', function() {
                this.classList.remove('drag-over');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('drag-over');
                if (e.dataTransfer.files.length) {
                    newInput.files = e.dataTransfer.files;
                    updateFileDisplay(newInput, currentFile);
                }
            });
            
            // Update display when file is selected
            newInput.addEventListener('change', function() {
                updateFileDisplay(this, currentFile);
            });
        }
    });
    
    function updateFileDisplay(input, displayElement) {
        if (input.files && input.files.length > 0) {
            const file = input.files[0];
            const fileSize = (file.size / (1024 * 1024)).toFixed(2); // MB
            
            displayElement.innerHTML = `
                <div style="margin-top: 10px; padding: 10px; background: #e8f5e9; border-radius: 5px;">
                    <strong>Selected file:</strong> ${file.name}<br>
                    <small>Size: ${fileSize} MB | Type: ${file.type}</small>
                </div>
            `;
            
            // If it's an audio file, show preview
            if (file.type.startsWith('audio/')) {
                const audioPreview = document.createElement('div');
                audioPreview.className = 'audio-preview-container';
                audioPreview.innerHTML = `
                    <h4><i class="fas fa-play-circle"></i> Audio Preview</h4>
                    <audio controls class="audio-player-custom">
                        <source src="${URL.createObjectURL(file)}" type="${file.type}">
                        Your browser does not support audio preview.
                    </audio>
                `;
                
                // Remove existing preview if any
                const existingPreview = displayElement.querySelector('.audio-preview-container');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                displayElement.appendChild(audioPreview);
            }
        } else {
            displayElement.innerHTML = '';
        }
    }
    
    // Duration calculator
    const minutesInput = document.querySelector('#id_duration_minutes');
    const secondsInput = document.querySelector('#id_duration_seconds');
    
    if (minutesInput && secondsInput) {
        const durationDisplay = document.createElement('div');
        durationDisplay.className = 'duration-display';
        durationDisplay.textContent = '00:00';
        
        secondsInput.parentNode.appendChild(durationDisplay);
        
        function updateDurationDisplay() {
            const minutes = minutesInput.value || 0;
            const seconds = secondsInput.value || 0;
            durationDisplay.textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        minutesInput.addEventListener('input', updateDurationDisplay);
        secondsInput.addEventListener('input', updateDurationDisplay);
        
        // Initial update
        updateDurationDisplay();
    }
    
    // Quality selector
    const qualitySelect = document.querySelector('#id_audio_quality');
    if (qualitySelect) {
        const qualityContainer = document.createElement('div');
        qualityContainer.className = 'quality-selector';
        
        const qualities = [
            { value: 'lossless', label: 'Lossless', desc: 'Best quality', badge: 'quality-lossless' },
            { value: 'high', label: 'High', desc: '320kbps', badge: 'quality-high' },
            { value: 'medium', label: 'Medium', desc: '192kbps', badge: 'quality-medium' }
        ];
        
        qualities.forEach(quality => {
            const option = document.createElement('div');
            option.className = 'quality-option';
            option.dataset.value = quality.value;
            
            option.innerHTML = `
                <h5>${quality.label}</h5>
                <p><small>${quality.desc}</small></p>
                <span class="quality-badge ${quality.badge}">${quality.label.toUpperCase()}</span>
            `;
            
            option.addEventListener('click', function() {
                qualitySelect.value = this.dataset.value;
                
                // Update visual selection
                qualityContainer.querySelectorAll('.quality-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                this.classList.add('selected');
            });
            
            qualityContainer.appendChild(option);
        });
        
        qualitySelect.style.display = 'none';
        qualitySelect.parentNode.appendChild(qualityContainer);
        
        // Set initial selection
        const initialOption = qualityContainer.querySelector(`[data-value="${qualitySelect.value}"]`);
        if (initialOption) {
            initialOption.classList.add('selected');
        }
    }
    
    // Lyrics editor enhancements
    const lyricsTextarea = document.querySelector('#id_lyrics');
    if (lyricsTextarea) {
        const editorContainer = document.createElement('div');
        editorContainer.className = 'lyrics-editor-container';
        
        const toolbar = document.createElement('div');
        toolbar.className = 'lyrics-toolbar';
        
        const buttons = [
            { icon: 'fas fa-bold', action: 'bold', title: 'Bold' },
            { icon: 'fas fa-italic', action: 'italic', title: 'Italic' },
            { icon: 'fas fa-underline', action: 'underline', title: 'Underline' },
            { icon: 'fas fa-heading', action: 'header', title: 'Header' },
            { icon: 'fas fa-list-ul', action: 'list', title: 'List' },
            { icon: 'fas fa-quote-left', action: 'quote', title: 'Quote' }
        ];
        
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.innerHTML = `<i class="${btn.icon}"></i>`;
            button.title = btn.title;
            button.type = 'button';
            
            button.addEventListener('click', function() {
                applyFormatting(btn.action);
            });
            
            toolbar.appendChild(button);
        });
        
        // Wrap the textarea
        lyricsTextarea.parentNode.insertBefore(editorContainer, lyricsTextarea);
        editorContainer.appendChild(toolbar);
        editorContainer.appendChild(lyricsTextarea);
        lyricsTextarea.classList.add('lyrics-textarea');
        
        function applyFormatting(action) {
            const start = lyricsTextarea.selectionStart;
            const end = lyricsTextarea.selectionEnd;
            const selectedText = lyricsTextarea.value.substring(start, end);
            
            let formattedText = selectedText;
            
            switch(action) {
                case 'bold':
                    formattedText = `**${selectedText}**`;
                    break;
                case 'italic':
                    formattedText = `*${selectedText}*`;
                    break;
                case 'underline':
                    formattedText = `__${selectedText}__`;
                    break;
                case 'header':
                    formattedText = `# ${selectedText}`;
                    break;
                case 'list':
                    formattedText = `- ${selectedText}`;
                    break;
                case 'quote':
                    formattedText = `> ${selectedText}`;
                    break;
            }
            
            lyricsTextarea.value = lyricsTextarea.value.substring(0, start) + 
                                  formattedText + 
                                  lyricsTextarea.value.substring(end);
            
            // Restore selection
            lyricsTextarea.selectionStart = start;
            lyricsTextarea.selectionEnd = start + formattedText.length;
            lyricsTextarea.focus();
        }
    }
    
    // Form validation enhancement
    const form = document.querySelector('#song_form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = '#e74c3c';
                    field.style.boxShadow = '0 0 0 3px rgba(231, 76, 60, 0.2)';
                    
                    // Add error message
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error-message')) {
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.style.color = '#e74c3c';
                        errorMsg.style.fontSize = '0.85rem';
                        errorMsg.style.marginTop = '5px';
                        errorMsg.textContent = 'This field is required';
                        field.parentNode.appendChild(errorMsg);
                    }
                    
                    isValid = false;
                } else {
                    field.style.borderColor = '';
                    field.style.boxShadow = '';
                    
                    // Remove error message
                    const errorMsg = field.parentNode.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('[required]:invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
                
                // Show notification
                showNotification('Please fill in all required fields marked with *', 'error');
            }
        });
    }
    
    // Notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        `;
        
        const colors = {
            success: '#2ecc71',
            error: '#e74c3c',
            info: '#3498db',
            warning: '#f39c12'
        };
        
        notification.style.background = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Add key shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitBtn = form.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
        
        // Escape to clear form
        if (e.key === 'Escape') {
            const clearBtn = form.querySelector('[type="reset"]');
            if (clearBtn) {
                if (confirm('Are you sure you want to clear the form?')) {
                    clearBtn.click();
                }
            }
        }
    });
});