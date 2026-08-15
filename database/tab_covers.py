# Book Covers tab logic

import json
import os
import urllib.parse
import streamlit as st
import requests
from PIL import Image
from io import BytesIO


def render_covers_tab(tab, geojson_client, all_books):
    """Render the Book Covers tab contents."""

    COVERS_GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "..", "vue-app", "public", "litmap-data.geojson")
    COVERS_DIR = os.path.join(os.path.dirname(__file__), "..", "vue-app", "public", "covers")
    MANIFEST_PATH = os.path.join(COVERS_DIR, "manifest.json")

    with tab:
        st.session_state.current_tab = "Book Covers"
        st.header("Book Covers")

        if "covers_cache_key" not in st.session_state:
            st.session_state.covers_cache_key = 0

        if not os.path.isfile(COVERS_GEOJSON_PATH):
            st.error(f"GeoJSON file not found at {COVERS_GEOJSON_PATH}")
            return

        @st.cache_data
        def load_covers_books(cache_key):
            """Load unique books from GeoJSON with cover metadata."""
            with open(COVERS_GEOJSON_PATH) as f:
                data = json.load(f)
            books = {}
            for feat in data["features"]:
                props = feat["properties"]
                bid = props.get("bookId", "")
                if bid and bid not in books:
                    cover_path = os.path.join(COVERS_DIR, f"{bid}.jpg")
                    books[bid] = {
                        "bookId": bid,
                        "title": props.get("title", ""),
                        "author": props.get("author", ""),
                        "has_cover_file": os.path.isfile(cover_path),
                        "cover_path": cover_path,
                    }
            return books

        def download_cover_from_url(url, book_id):
            """Download image from URL, validate, and save as JPEG."""
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            if img.width < 10 or img.height < 10:
                return False, "Image too small (likely a placeholder)"
            img = img.convert("RGB")
            save_path = os.path.join(COVERS_DIR, f"{book_id}.jpg")
            img.save(save_path, "JPEG", quality=85)
            return True, save_path

        def update_manifest_and_geojson(book_id):
            """Add entry to manifest.json and set hasCover=true in GeoJSON."""
            manifest = {}
            if os.path.isfile(MANIFEST_PATH):
                with open(MANIFEST_PATH) as f:
                    manifest = json.load(f)
            manifest[book_id] = f"{book_id}.jpg"
            with open(MANIFEST_PATH, "w") as f:
                json.dump(manifest, f, indent=2)

            # Read fresh GeoJSON from disk
            with open(COVERS_GEOJSON_PATH) as f:
                geojson_data = json.load(f)
            for feat in geojson_data["features"]:
                if feat["properties"].get("bookId") == book_id:
                    feat["properties"]["hasCover"] = True
            with open(COVERS_GEOJSON_PATH, "w") as f:
                json.dump(geojson_data, f, indent=2)

        covers_books = load_covers_books(st.session_state.covers_cache_key)
        total = len(covers_books)
        has_cover = sum(1 for b in covers_books.values() if b["has_cover_file"])
        missing = total - has_cover

        # Metrics row
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total Books", total)
        mc2.metric("Has Cover", has_cover)
        mc3.metric("Missing", missing)

        # Filter
        cover_filter = st.radio(
            "Filter books:",
            ["All", "Missing Cover only", "Has Cover only"],
            horizontal=True,
            key="covers_filter",
        )

        if cover_filter == "Missing Cover only":
            filtered = {k: v for k, v in covers_books.items() if not v["has_cover_file"]}
        elif cover_filter == "Has Cover only":
            filtered = {k: v for k, v in covers_books.items() if v["has_cover_file"]}
        else:
            filtered = covers_books

        # Sort by title
        sorted_books = sorted(filtered.values(), key=lambda b: b["title"].lower())
        st.write(f"Showing {len(sorted_books)} books")

        for book in sorted_books:
            icon = "V" if book["has_cover_file"] else "X"
            label = f"[{icon}] {book['title']} -- {book['author']}"
            with st.expander(label):
                st.text(f"Book ID: {book['bookId']}")

                # Current cover
                if book["has_cover_file"]:
                    st.image(book["cover_path"], width=120)
                else:
                    st.info("No cover image on file")

                # Search links
                title_enc = urllib.parse.quote(book["title"])
                author_enc = urllib.parse.quote(book["author"])
                lc1, lc2 = st.columns(2)
                with lc1:
                    st.link_button(
                        "Find on Goodreads",
                        f"https://www.goodreads.com/search?q={title_enc}+{author_enc}",
                        use_container_width=True,
                    )
                with lc2:
                    st.link_button(
                        "Find on Google Images",
                        f"https://www.google.com/search?tbm=isch&q=%22{title_enc}%22+%22{author_enc}%22+book+cover",
                        use_container_width=True,
                    )

                # URL input and preview
                url_key = f"cover_url_{book['bookId']}"
                cover_url = st.text_input("Paste Cover Image URL:", key=url_key)

                preview_key = f"cover_preview_{book['bookId']}"
                previewing = st.session_state.get(preview_key, False)

                if cover_url:
                    if st.button("Preview", key=f"cover_prev_btn_{book['bookId']}"):
                        st.session_state[preview_key] = True
                        previewing = True

                if previewing and cover_url:
                    st.markdown(f'<img src="{cover_url}" width="120">', unsafe_allow_html=True)

                # Download & Save button
                btn_key = f"cover_save_{book['bookId']}"
                if st.button("Download & Save", key=btn_key, disabled=not (previewing and cover_url)):
                    try:
                        with st.spinner("Downloading cover..."):
                            success, result = download_cover_from_url(cover_url, book["bookId"])
                        if success:
                            update_manifest_and_geojson(book["bookId"])
                            st.toast(f"Cover saved for {book['title']}", icon="V")
                            st.session_state.covers_cache_key += 1
                            st.session_state.pop(preview_key, None)
                            st.rerun()
                        else:
                            st.error(result)
                    except Exception as e:
                        st.error(f"Failed to download cover: {e}")
