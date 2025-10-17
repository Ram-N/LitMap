
# Streamlit to Manage Firestore DB

I use a streamlit app (run locally) to update the fireStore DB that stores all the data for LitMap.
The main purpose of this app is to help me with DB MGMT.
```
> source activate <relevant env> litmap
> streamlit run main.py
```

# Coding Tasks Remaining

In search, make sure "Enter" button works.

## New Dropdown fields needed
- PURGE - write and delete
- Duplicates related


1. Add a new location to a book
2. Add a location description to a book

# Get and Print Functions

- When listing a book, write all its attributes...

## Handle Dupes
    - First reconcile the two books, giving the first ID all the good attributes.
    - Next Delete the second book, based on its ID.
    - verify that the book doesn't exist anymore.




