# Book Detail Page — generates a self-contained HTML view of a single book

import base64
import os
import html


def generate_book_detail_html(book):
    """
    Generate a complete self-contained HTML string for displaying a book's details.

    Uses Leaflet (OpenStreetMap) for the embedded map — no API key required.

    Args:
        book: dict with keys like id, title, author, description, booktype, genre,
              tags, rating, pageCount, publisher, year, language, isbn, cover,
              hasCover, goodreadsLink, locations[]

    Returns:
        str: Complete HTML document string with inline CSS/JS.
    """
    book_id = book.get('id', '')
    title = html.escape(book.get('title', 'Untitled'))
    author = html.escape(book.get('author', 'Unknown Author'))
    description = html.escape(book.get('description', '') or '')
    booktype = html.escape(book.get('booktype', '') or '')
    genre = html.escape(book.get('genre', '') or '')
    rating = book.get('rating')
    page_count = book.get('pageCount')
    publisher = html.escape(str(book.get('publisher', '') or ''))
    year = book.get('year', '')
    language = html.escape(book.get('language', '') or '')
    isbn = book.get('isbn', '') or ''
    isbn10 = book.get('isbn10', '') or ''
    asin = book.get('asin', '') or ''
    goodreads_link = book.get('goodreadsLink', '') or ''
    locations = book.get('locations', [])
    tags = book.get('tags', [])

    # Build cover image
    cover_img_src = _get_cover_image_src(book)

    # Build tags display
    tags_html = ''
    if tags and isinstance(tags, list) and any(tags):
        tag_spans = ' '.join(
            f'<span class="tag">{html.escape(str(t))}</span>' for t in tags if t
        )
        tags_html = f'<div class="tags">Tags: {tag_spans}</div>'

    # Build meta line (booktype, genre, rating)
    meta_parts = []
    if booktype:
        meta_parts.append(booktype.capitalize())
    if genre:
        meta_parts.append(genre)
    if rating:
        try:
            meta_parts.append(f'Rating: {float(rating):.1f}/5')
        except (ValueError, TypeError):
            pass
    meta_line = ' &middot; '.join(meta_parts)

    # Build publication details
    pub_parts = []
    if publisher:
        pub_parts.append(f'<strong>Publisher:</strong> {publisher}')
    if year:
        pub_parts.append(f'<strong>Year:</strong> {year}')
    if page_count:
        pub_parts.append(f'<strong>Pages:</strong> {page_count}')
    pub_line = '  |  '.join(pub_parts)

    id_parts = []
    if isbn:
        id_parts.append(f'<strong>ISBN:</strong> {html.escape(str(isbn))}')
    if isbn10:
        id_parts.append(f'<strong>ISBN-10:</strong> {html.escape(str(isbn10))}')
    if asin:
        id_parts.append(f'<strong>ASIN:</strong> {html.escape(str(asin))}')
    id_line = '  |  '.join(id_parts)

    goodreads_html = ''
    if goodreads_link:
        goodreads_html = f'<div class="goodreads"><strong>Goodreads:</strong> <a href="{html.escape(goodreads_link)}" target="_blank">{html.escape(goodreads_link)}</a></div>'

    # Build locations list and map markers JS
    locations_html = ''
    markers_js = ''
    if locations:
        loc_items = []
        marker_lines = []
        for i, loc in enumerate(locations, 1):
            city = loc.get('city', '')
            country = loc.get('country', '')
            lat = loc.get('latitude', 0)
            lng = loc.get('longitude', 0)
            loc_desc = loc.get('description', '')

            place = ', '.join(p for p in [city, country] if p)
            coord_str = f'({lat}, {lng})'
            desc_str = f' — {html.escape(loc_desc)}' if loc_desc else ''
            loc_items.append(f'<div class="location-item">{i}. {html.escape(place)} {coord_str}{desc_str}</div>')

            popup = html.escape(place).replace("'", "\\'")
            marker_lines.append(
                f"L.marker([{lat}, {lng}]).addTo(map).bindPopup('{popup}');"
            )

        locations_html = '\n'.join(loc_items)

        # Build bounds fitting JS
        coords_array = ', '.join(f'[{loc.get("latitude", 0)}, {loc.get("longitude", 0)}]' for loc in locations)
        markers_js = '\n'.join(marker_lines)
        markers_js += f"""
var bounds = L.latLngBounds([{coords_array}]);
map.fitBounds(bounds, {{padding: [30, 30], maxZoom: 10}});
"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #fff; padding: 20px; }}
.header {{ display: flex; gap: 20px; margin-bottom: 20px; }}
.cover {{ flex-shrink: 0; }}
.cover img {{ width: 140px; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
.cover .placeholder {{ width: 140px; height: 200px; background: #e0e0e0; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 13px; text-align: center; padding: 10px; }}
.header-info {{ flex: 1; }}
.header-info h1 {{ font-size: 22px; margin-bottom: 4px; color: #1a1a1a; }}
.header-info .author {{ font-size: 16px; color: #555; margin-bottom: 8px; }}
.header-info .meta {{ font-size: 14px; color: #777; margin-bottom: 8px; }}
.tags {{ margin-top: 8px; }}
.tag {{ display: inline-block; background: #e8f4f8; color: #2980b9; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 4px; margin-bottom: 4px; }}
.section {{ border-top: 1px solid #eee; padding: 16px 0; }}
.section h2 {{ font-size: 16px; color: #444; margin-bottom: 8px; }}
.section p {{ font-size: 14px; line-height: 1.6; color: #555; }}
.pub-details {{ font-size: 14px; color: #555; line-height: 1.8; }}
.goodreads a {{ color: #2980b9; text-decoration: none; }}
.goodreads a:hover {{ text-decoration: underline; }}
#map {{ width: 100%; height: 350px; border-radius: 6px; margin-bottom: 12px; border: 1px solid #ddd; }}
.location-item {{ font-size: 13px; color: #555; padding: 2px 0; }}
</style>
</head>
<body>

<div class="header">
  <div class="cover">
    {f'<img src="{cover_img_src}" alt="Cover">' if cover_img_src else '<div class="placeholder">No Cover Available</div>'}
  </div>
  <div class="header-info">
    <h1>{title}</h1>
    <div class="author">{author}</div>
    <div class="meta">{meta_line}</div>
    {tags_html}
  </div>
</div>

{'<div class="section"><h2>Description</h2><p>' + description.replace(chr(10), '<br>') + '</p></div>' if description else ''}

<div class="section">
  <h2>Publication Details</h2>
  <div class="pub-details">
    {f'<div>{pub_line}</div>' if pub_line else ''}
    {f'<div><strong>Language:</strong> {language}</div>' if language else ''}
    {f'<div>{id_line}</div>' if id_line else ''}
    {goodreads_html}
  </div>
</div>

{'<div class="section"><h2>Locations</h2><div id="map"></div>' + locations_html + '</div>' if locations else ''}

<script>
{f"""
var map = L.map('map').setView([20, 0], 2);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18
}}).addTo(map);
{markers_js}
""" if locations else ""}
</script>

</body>
</html>"""


def _get_cover_image_src(book):
    """Determine the best cover image source for the book."""
    book_id = book.get('id', '')
    has_cover = book.get('hasCover', False)
    isbn = book.get('isbn', '') or ''

    # Try local cover file
    if has_cover and book_id:
        cover_path = os.path.join(
            os.path.dirname(__file__), '..', 'vue-app', 'public', 'covers', f'{book_id}.jpg'
        )
        if os.path.isfile(cover_path):
            try:
                with open(cover_path, 'rb') as f:
                    img_data = f.read()
                b64 = base64.b64encode(img_data).decode('utf-8')
                return f'data:image/jpeg;base64,{b64}'
            except Exception:
                pass

    # Fallback: Open Library cover by ISBN
    if isbn:
        clean_isbn = str(isbn).strip()
        if clean_isbn and clean_isbn.lower() not in ('na', 'none', 'null'):
            return f'https://covers.openlibrary.org/b/isbn/{clean_isbn}-M.jpg'

    return None
