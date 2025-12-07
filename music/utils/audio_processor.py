# music/utils/audio_processor.py
import os
from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TDRC
from PIL import Image, ImageDraw, ImageFont
import io

def add_logo_to_cover(cover_path, logo_path, output_path):
    """Add logo to song cover image"""
    try:
        # Open cover image
        cover = Image.open(cover_path).convert('RGBA')
        
        # Open logo and resize
        logo = Image.open(logo_path).convert('RGBA')
        logo_size = (cover.width // 4, cover.height // 4)  # 25% of cover size
        logo = logo.resize(logo_size, Image.Resampling.LANCZOS)
        
        # Position logo in bottom right corner
        position = (cover.width - logo.width - 20, cover.height - logo.height - 20)
        
        # Create transparent overlay
        overlay = Image.new('RGBA', cover.size, (0, 0, 0, 0))
        overlay.paste(logo, position)
        
        # Combine images
        result = Image.alpha_composite(cover, overlay)
        result = result.convert('RGB')  # Convert back to RGB for JPEG
        result.save(output_path, 'JPEG', quality=85)
        
        return True
    except Exception as e:
        print(f"Error adding logo to cover: {e}")
        return False

def add_metadata_to_audio(audio_path, song, cover_path=None, logo_path=None):
    """Add metadata and branded cover to audio file"""
    try:
        audio = File(audio_path)
        
        # Ensure ID3 tags exist
        if audio.tags is None:
            audio.add_tags()
        
        # Add basic metadata
        audio.tags.add(TIT2(encoding=3, text=song.title))
        audio.tags.add(TPE1(encoding=3, text=song.artist.name))
        audio.tags.add(TCON(encoding=3, text=song.genre.name if song.genre else ""))
        audio.tags.add(TDRC(encoding=3, text=str(song.release_year) if song.release_year else ""))
        
        # Handle cover art
        if cover_path and os.path.exists(cover_path):
            # Add logo to cover if provided
            if logo_path and os.path.exists(logo_path):
                temp_cover_path = f"/tmp/branded_cover_{song.id}.jpg"
                if add_logo_to_cover(cover_path, logo_path, temp_cover_path):
                    cover_path = temp_cover_path
            
            # Add cover art to audio file
            with open(cover_path, 'rb') as cover_file:
                cover_data = cover_file.read()
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover image
                    desc='Cover',
                    data=cover_data
                ))
        
        # Save metadata
        audio.save()
        
        # Clean up temporary file
        if 'temp_cover_path' in locals() and os.path.exists(temp_cover_path):
            os.remove(temp_cover_path)
            
        return True
    except Exception as e:
        print(f"Error adding metadata: {e}")
        return False