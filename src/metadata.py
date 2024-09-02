from src.logging import ActionLogger

class Metadata:
    def __init__(self, references):
        self.theme = references["Theme"]
        self.author = references["Author"]
        self.title = references["Title"]
        self.publisher = references["Publisher"]
        self.year = references["Year"]
        self.logger = ActionLogger(self.theme, self.title)

    def add_metadata(self, documents, metadata):
        """Add metadata to each item (document or node)."""
        for document in documents:
            if not hasattr(document, 'metadata') or document.metadata is None:
                document.metadata = {}
            document.metadata.update(metadata)
            print("metadata is added")
            # self.logger.log_action(f"Metadata added to document {item.id_}", action_type="METADATA")

        return documents

    def _generate_metadata(self):
        """Generate metadata and return it."""
        metadata = {
            "theme": self.theme,
            "author": self.author,
            "title": self.title,
            "publisher": self.publisher,
            "year": self.year,
            "reference": f"{self.author}. ({self.year}). *{self.title}*. {self.publisher}."  # APA style reference
        }
        print("metadata is generated")
        return metadata

    def apply_metadata(self, documents):
        """Apply generated metadata to documents."""
        metadata = self._generate_metadata()
        print("metada is applied")
        return self.add_metadata(documents, metadata)