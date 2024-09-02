import json

class SummarizationDeck:
    def __init__(self, title, summarizations):
        self.title = title
        self.summarizations = summarizations

    def to_dict(self):
        return {
            'title': self.title,
            'summarizations': [summarization.to_dict() for summarization in self.summarizations]
        }

    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.to_dict(), file, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            summarization = [Summarizer(**summarization_data) for summarization_data in data['summarizations']]
            return cls(data['title'], summarization)


class Summarizer:
    def __init__(self, title, topic, subtopic, summarization):
        self.title = title
        self.topic = topic
        self.subtopic = subtopic
        self.summarization = summarization

    def to_dict(self):
        return {
            'title': self.title,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'summarization': self.summarization
        }
        
    def render(self, display_narration=False):
        markdown_text = f"# {self.topic}\n## {self.subtopic}\n"
        markdown_text += f"{self.summarization.strip()}\n\n"
        if display_narration:
            markdown_text += "---\n\n\n"  # Separator line
            markdown_text += f"*{self.subtopic}*"
        return markdown_text