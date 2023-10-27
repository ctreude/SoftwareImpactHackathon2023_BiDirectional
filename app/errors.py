class LatexMergedNotFound(Exception):
    def __init__(self):
        message = "Cannot find any `merged.tex` file. Did you run the merger first?"
        super().__init__(message)


class PDFsExtractedNotFound(Exception):
    def __init__(self):
        message = (
            "Cannot find any `extracted.txt` file. Did you run the extraction first?"
        )
        super().__init__(message)
