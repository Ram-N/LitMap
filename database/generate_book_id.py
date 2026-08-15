"""Generate human-readable book IDs from ISBN or title+author slugs."""

import re
import unicodedata


def normalize_isbn(isbn_str):
    """Normalize an ISBN string to ISBN-13.

    Strips hyphens, converts ISBN-10 to ISBN-13 with check digit validation.
    Returns None for empty, "NA", "None", or invalid values.
    """
    if not isbn_str or str(isbn_str).strip().lower() in ("na", "none", "null", ""):
        return None

    digits = re.sub(r"[^0-9Xx]", "", str(isbn_str).strip())

    if len(digits) == 13:
        if _valid_isbn13(digits):
            return digits
        return None

    if len(digits) == 10:
        return _isbn10_to_isbn13(digits)

    return None


def _valid_isbn13(digits):
    """Check ISBN-13 check digit."""
    total = sum(
        int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12])
    )
    check = (10 - (total % 10)) % 10
    return check == int(digits[12])


def _isbn10_to_isbn13(digits):
    """Convert ISBN-10 to ISBN-13. Returns None if ISBN-10 check digit is invalid."""
    # Validate ISBN-10 check digit first
    total = 0
    for i, ch in enumerate(digits[:9]):
        total += int(ch) * (10 - i)
    last = digits[9].upper()
    check_val = 10 if last == "X" else int(last)
    total += check_val
    if total % 11 != 0:
        return None

    # Convert: prepend 978, recalculate check digit
    base = "978" + digits[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
    check = (10 - (total % 10)) % 10
    return base + str(check)


def slugify(text):
    """Convert text to a URL-friendly slug.

    Transliterates unicode, lowercases, replaces non-alphanumeric with hyphens.
    """
    # Normalize unicode characters (e.g., é -> e)
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    return text


def generate_book_id(title, author, isbn):
    """Generate a human-readable book ID.

    Uses ISBN-13 if available, otherwise a title-author slug.
    Returns None if both title and author are missing.
    """
    # Try ISBN first
    normalized = normalize_isbn(isbn)
    if normalized:
        return normalized

    # Fall back to slug
    if not title and not author:
        return None

    title = str(title) if title else ""
    author = str(author) if author else ""

    # Strip subtitle (after colon)
    title_main = title.split(":")[0].strip()
    title_slug = slugify(title_main)

    # Truncate title slug to ~50 chars at word boundary
    if len(title_slug) > 50:
        parts = title_slug[:50].split("-")
        # Drop the last partial word
        if len(parts) > 1:
            title_slug = "-".join(parts[:-1])
        else:
            title_slug = parts[0]

    # Use author's last name only
    author_parts = author.strip().split()
    surname = slugify(author_parts[-1]) if author_parts else ""

    if title_slug and surname:
        return f"{title_slug}-{surname}"
    elif title_slug:
        return title_slug
    elif surname:
        return surname

    return None
