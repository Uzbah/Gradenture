import re

# NUL and other C0 control chars (keeping \t \n \r): Postgres text rejects \x00
# outright, and the rest are never legitimate in user prose.
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(text: str) -> str:
    # ponytail: no HTML stripping. Text is only ever rendered via React (escaped)
    # or sent as plain-text email, and stripping "<...>" destroyed code like
    # vector<int> in interview questions. Strip HTML here only if a field is
    # ever rendered as HTML.
    return _CONTROL.sub("", text)
