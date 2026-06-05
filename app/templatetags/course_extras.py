import re
from django import template

register = template.Library()

@register.filter
def youtube_embed(url):
    """
    Converts various YouTube URL formats into a clean embed URL.
    Handles:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - and URLs with extra parameters.
    """
    if not url:
        return ""
    
    # Regex to capture the video ID (11 characters)
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)
    
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    
    return url
