from transformers import pipeline
import re #re stands for regular expressions which is a tool for finding and replacing patterns of text

class ThemeAnalyzer:
    def __init__(self):
        # Initalize zero-shot classification model
        self.classifer = pipeline("zero-shot-classification",
                         model = "facebook/bart-large-mnli")

        #Predefined themes
        self.themes = {
            'party': ['party', 'celebration', 'dancing', 'club', 'fun'],
            'workout': ['energy', 'motivation', 'power', 'strength', 'intense'],
            'relaxation': ['calm', 'peaceful', 'chill', 'ambient', 'meditation'],
            'romance': ['love', 'romantic', 'intimate', 'passionate', 'emotional'],
            'melancholy': ['sad', 'melancholic', 'nostalgic', 'blues', 'heartbreak'],
            'focus': ['concentration', 'study', 'work', 'productivity', 'ambient'],
            'road_trip': ['driving', 'journey', 'adventure', 'freedom', 'wanderlust'],
            'sleep': ['sleep', 'lullaby', 'night', 'dreams', 'peaceful']
        }

    def analyze_theme(self, text, custom_themes=None):
        """
        Analyze text (track name, description, lyrics) for themes
        Returns theme scores
        """

        if custom_themes:
            candidate_labels = custom_themes
        
        else:
            candidate_labels = list(self.themes.keys())

        # Clean text
        text = self.clean_text(text)

        if not text:
            return {}

        # Classify:
        result = self.classifier(text, candidate_labels)

        # Return as dictionary
        return {
            label: score
            
            for label, score in zip(result['labels'], result['scores'])
        }

    def clean_text(self, text):
        """Clean and prepare text for analysis"""

        # Remove special characters, extra spaces
        text = re.sub(r'[^\w\s]','',text)
        text = re.sub(r'\s+','',text)
        return text.strip().lower()

    def get_theme_keywords(self, theme):
        """Get keywords associated with a theme"""
        return self.themes.get(theme, [])
