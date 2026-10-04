import re

_TAG_RE = re.compile(r'<[^>]*>')


def clean_text(text: str) -> str:
    """Strip HTML tags from user-submitted text before it is stored.

    Applied by the service layer to every free-text field a user can write.
    """
    return _TAG_RE.sub('', text)
