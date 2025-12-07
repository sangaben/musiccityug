from django.shortcuts import render

def help_center(request):
    """Help center page"""
    faqs = [
        {
            'question': 'How do I upload my music?',
            'answer': 'Go to your artist dashboard and click "Upload Music". You need to be verified as an artist to upload songs.'
        },
        {
            'question': 'Can I download songs for offline listening?',
            'answer': 'Yes! Offline downloading is available for Premium and Premium Plus subscribers.'
        },
        {
            'question': 'How do I create a playlist?',
            'answer': 'Go to your Library page and click "Create Playlist". You can add songs from the discover page or search results.'
        },
        {
            'question': 'What audio formats are supported?',
            'answer': 'We support MP3, WAV, and OGG formats for audio files.'
        },
        {
            'question': 'How do I become a verified artist?',
            'answer': 'Contact our support team with your artist information and portfolio for verification.'
        },
        {
            'question': 'Can I cancel my premium subscription?',
            'answer': 'Yes, you can cancel anytime from your account settings. Your premium features will remain active until the end of your billing period.'
        }
    ]
    
    context = {
        'faqs': faqs,
    }
    return render(request, 'help/help_center.html', context)
    
