# ISBN Manager tab logic

import json
import re
import os
import urllib.parse
import streamlit as st


def render_isbn_tab(tab, geojson_client, all_books):
    """Render the ISBN Manager tab contents."""

    ISBN_GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "..", "vue-app", "public", "litmap-data.geojson")

    with tab:
        st.session_state.current_tab = "ISBN Manager"
        st.header("ISBN Manager")

        if not os.path.exists(ISBN_GEOJSON_PATH):
            st.error(f"GeoJSON file not found at {ISBN_GEOJSON_PATH}")
            return

        books_dict, full_geojson = _load_geojson_books(ISBN_GEOJSON_PATH)
        isbn_all_books = list(books_dict.values())

        # Classify each book
        for b in isbn_all_books:
            isbn_val = b["isbn"]
            if not isbn_val or str(isbn_val).strip().lower() in ("na", "none", "null", ""):
                b["status"] = "Missing"
            else:
                valid, _ = _validate_isbn(isbn_val)
                b["status"] = "Valid" if valid else "Invalid"

        total = len(isbn_all_books)
        valid_count = sum(1 for b in isbn_all_books if b["status"] == "Valid")
        missing_count = sum(1 for b in isbn_all_books if b["status"] == "Missing")
        invalid_count = sum(1 for b in isbn_all_books if b["status"] == "Invalid")

        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Books", total)
        col2.metric("Valid ISBN", valid_count)
        col3.metric("Missing ISBN", missing_count)
        col4.metric("Invalid ISBN", invalid_count)

        # Filter
        filter_opt = st.selectbox("Filter", ["All", "Missing ISBN only", "Invalid ISBN only"], key="isbn_filter")
        if filter_opt == "Missing ISBN only":
            display_books = [b for b in isbn_all_books if b["status"] == "Missing"]
        elif filter_opt == "Invalid ISBN only":
            display_books = [b for b in isbn_all_books if b["status"] == "Invalid"]
        else:
            display_books = isbn_all_books

        st.write(f"Showing {len(display_books)} books")

        # Initialize session state for ISBN edits
        if "isbn_edits" not in st.session_state:
            st.session_state.isbn_edits = {}
        if "isbn10_edits" not in st.session_state:
            st.session_state.isbn10_edits = {}
        if "asin_edits" not in st.session_state:
            st.session_state.asin_edits = {}

        # Show pending changes count and save button at the top
        _all_edited_top = set(st.session_state.isbn_edits) | set(st.session_state.isbn10_edits) | set(st.session_state.asin_edits)
        if _all_edited_top:
            st.info(f"**{len(_all_edited_top)} book(s) with pending changes** -- scroll down or use the Save button below.")
            if st.button("Save Changes to GeoJSON", type="primary", key="save_top"):
                st.session_state['_isbn_save_triggered'] = True
                st.rerun()

        # Display books in an editable table
        for i, book in enumerate(display_books):
            bid = book["bookId"]
            status_icon = {"Valid": "V", "Missing": "X", "Invalid": "!"}.get(book["status"], "")

            with st.expander(f"[{status_icon}] {book['title']} -- {book['author']}"):
                st.write(f"**Book ID:** `{bid}`")
                st.write(f"**Current ISBN:** `{book['isbn']}`  |  **ISBN-10:** `{book.get('isbn10')}`  |  **ASIN:** `{book.get('asin')}`")
                st.write(f"**Status:** {book['status']}")

                # --- Paste from Goodreads ---
                st.markdown("---")
                st.markdown("##### Paste from Goodreads")
                pasted = st.text_area(
                    "Paste edition details from Goodreads",
                    key=f"paste_{bid}",
                    height=100,
                    placeholder="ISBN\n9780618155477 (ISBN10: 0618155473)\nASIN\n0618155473"
                )
                # Show parse result message from previous run
                parse_msg_key = f"parse_msg_{bid}"
                if parse_msg_key in st.session_state:
                    msg_type, msg_text = st.session_state.pop(parse_msg_key)
                    if msg_type == "success":
                        st.success(msg_text)
                    elif msg_type == "warning":
                        st.warning(msg_text)

                if st.button("Parse & Fill", key=f"parse_{bid}"):
                    parsed = _parse_goodreads_text(pasted)
                    if parsed:
                        if 'isbn' in parsed:
                            st.session_state.isbn_edits[bid] = parsed['isbn']
                            st.session_state[f"isbn_input_{bid}"] = parsed['isbn']
                        if 'isbn10' in parsed:
                            st.session_state.setdefault('isbn10_edits', {})[bid] = parsed['isbn10']
                            st.session_state[f"isbn10_input_{bid}"] = parsed['isbn10']
                        if 'asin' in parsed:
                            st.session_state.setdefault('asin_edits', {})[bid] = parsed['asin']
                            st.session_state[f"asin_input_{bid}"] = parsed['asin']
                        found = [f"**{k}**: `{v}`" for k, v in parsed.items()]
                        not_found = [f for f in ('isbn', 'isbn10', 'asin') if f not in parsed]
                        msg = "Found: " + " | ".join(found)
                        if not_found:
                            msg += f"  \nNot found in text: {', '.join(not_found)}"
                        st.session_state[parse_msg_key] = ("success", msg)
                        st.rerun()
                    else:
                        st.session_state[parse_msg_key] = ("warning", "Could not parse any ISBN or ASIN from the pasted text. Expected lines like 'ISBN 9780618155477 (ISBN10: 0618155473)' or 'ASIN B01MQIPIT5'.")
                        st.rerun()

                st.markdown("---")

                # Editable ISBN input
                current_val = st.session_state.isbn_edits.get(bid, str(book["isbn"] or ""))
                new_isbn = st.text_input("ISBN-13", value=current_val, key=f"isbn_input_{bid}")

                if new_isbn != current_val:
                    st.session_state.isbn_edits[bid] = new_isbn

                # Real-time validation
                if new_isbn:
                    valid, normalized = _validate_isbn(new_isbn)
                    if valid:
                        st.success(f"Valid ISBN-13: {normalized}")
                        st.session_state.isbn_edits[bid] = new_isbn
                    else:
                        st.error("Invalid ISBN check digit")

                # Editable ISBN-10 input
                current_isbn10 = st.session_state.get('isbn10_edits', {}).get(bid, str(book.get("isbn10") or ""))
                new_isbn10 = st.text_input("ISBN-10", value=current_isbn10, key=f"isbn10_input_{bid}")
                if new_isbn10 != current_isbn10:
                    st.session_state.setdefault('isbn10_edits', {})[bid] = new_isbn10

                # Editable ASIN input
                current_asin = st.session_state.get('asin_edits', {}).get(bid, str(book.get("asin") or ""))
                new_asin = st.text_input("ASIN", value=current_asin, key=f"asin_input_{bid}")
                if new_asin != current_asin:
                    st.session_state.setdefault('asin_edits', {})[bid] = new_asin

                # Action buttons row
                col_gr, col_ol, col_save = st.columns(3)

                with col_gr:
                    goodreads_query = urllib.parse.quote(f"{book['title']} {book['author']}")
                    goodreads_url = f"https://www.goodreads.com/search?q={goodreads_query}"
                    st.link_button("Goodreads", goodreads_url, key=f"goodreads_{bid}")

                with col_save:
                    if st.button("Save", key=f"save_{bid}", type="primary"):
                        st.session_state['_isbn_save_triggered'] = True
                        st.rerun()

                # Open Library lookup button
                with col_ol:
                    lookup_clicked = st.button("Open Library", key=f"lookup_{bid}")
                if lookup_clicked:
                    results = _lookup_openlibrary(book["title"], book["author"])
                    if results:
                        for r in results:
                            st.write(f"  **{r['title']}** by {r['author']}")
                            st.code(r["isbn"])
                            if len(r["all_isbns"]) > 1:
                                st.write(f"  Other ISBNs: {', '.join(r['all_isbns'][1:])}")
                    else:
                        st.info("No results found on Open Library")

        # Save button
        st.divider()
        isbn_edits = st.session_state.get('isbn_edits', {})
        isbn10_edits = st.session_state.get('isbn10_edits', {})
        asin_edits = st.session_state.get('asin_edits', {})
        all_edited_bids = set(isbn_edits) | set(isbn10_edits) | set(asin_edits)

        save_from_top = st.session_state.pop('_isbn_save_triggered', False)

        if all_edited_bids:
            st.write(f"**{len(all_edited_bids)} book(s) with pending changes**")
            if save_from_top or st.button("Save Changes to GeoJSON", type="primary", key="save_bottom"):
                updated = 0
                for feat in full_geojson["features"]:
                    bid = feat["properties"].get("bookId", "")
                    changed = False
                    if bid in isbn_edits and isbn_edits[bid]:
                        feat["properties"]["isbn"] = isbn_edits[bid]
                        changed = True
                    if bid in isbn10_edits and isbn10_edits[bid]:
                        feat["properties"]["isbn10"] = isbn10_edits[bid]
                        changed = True
                    if bid in asin_edits and asin_edits[bid]:
                        feat["properties"]["asin"] = asin_edits[bid]
                        changed = True
                    if changed:
                        updated += 1

                with open(ISBN_GEOJSON_PATH, "w") as f:
                    json.dump(full_geojson, f, indent=2)

                st.success(f"Saved updates across {updated} feature(s) to GeoJSON")
                st.session_state.isbn_edits = {}
                st.session_state.isbn10_edits = {}
                st.session_state.asin_edits = {}
                st.rerun()
        else:
            st.info("No pending changes. Edit ISBNs above to make changes.")


# --- Local helper functions ---

def _load_geojson_books(geojson_path):
    """Load unique books from the GeoJSON file."""
    with open(geojson_path) as f:
        data = json.load(f)
    books = {}
    for feat in data["features"]:
        props = feat["properties"]
        bid = props.get("bookId", "")
        if bid and bid not in books:
            books[bid] = {
                "bookId": bid,
                "title": props.get("title", ""),
                "author": props.get("author", ""),
                "isbn": props.get("isbn"),
                "isbn10": props.get("isbn10"),
                "asin": props.get("asin"),
            }
    return books, data


def _parse_goodreads_text(text):
    """Parse pasted Goodreads edition details to extract ISBN, ISBN10, and ASIN."""
    result = {}
    isbn13_match = re.search(r'\b(97[89]\d{10})\b', text)
    if isbn13_match:
        result['isbn'] = isbn13_match.group(1)
    isbn10_match = re.search(r'ISBN10[:\s]+([0-9Xx]{10})', text)
    if isbn10_match:
        result['isbn10'] = isbn10_match.group(1)
    asin_match = re.search(r'ASIN[:\s]+([A-Z0-9]{10})', text)
    if asin_match:
        result['asin'] = asin_match.group(1)
    return result


def _validate_isbn(isbn_str):
    """Validate an ISBN using check digit algorithm. Returns (is_valid, normalized)."""
    if not isbn_str or str(isbn_str).strip().lower() in ("na", "none", "null", ""):
        return False, None
    digits = re.sub(r"[^0-9Xx]", "", str(isbn_str).strip())
    if len(digits) == 13:
        total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
        check = (10 - (total % 10)) % 10
        if check == int(digits[12]):
            return True, digits
        return False, None
    if len(digits) == 10:
        total = 0
        for i, ch in enumerate(digits[:9]):
            total += int(ch) * (10 - i)
        last = digits[9].upper()
        check_val = 10 if last == "X" else int(last)
        total += check_val
        if total % 11 == 0:
            base = "978" + digits[:9]
            t = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(base))
            c = (10 - (t % 10)) % 10
            return True, base + str(c)
        return False, None
    return False, None


def _lookup_openlibrary(title, author):
    """Search Open Library API for ISBNs by title and author."""
    import urllib.request
    query = f"{title} {author}"
    url = f"https://openlibrary.org/search.json?q={urllib.parse.quote(query)}&limit=5"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        results = []
        for doc in data.get("docs", []):
            isbns = doc.get("isbn", [])
            if isbns:
                results.append({
                    "title": doc.get("title", ""),
                    "author": ", ".join(doc.get("author_name", [])),
                    "isbn": isbns[0],
                    "all_isbns": isbns[:5],
                })
        return results
    except Exception as e:
        st.error(f"Open Library lookup failed: {e}")
        return []
