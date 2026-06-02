import re

def clean_input(text: str) -> str:
    text = text.lower().strip()
    # Remove excessive punctuation but preserve dots, hyphens, underscores
    text = re.sub(r'[^\w\s.\-_]', '', text)
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)
    return text
