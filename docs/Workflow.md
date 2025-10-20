## Workflow

cd LitMap
firebase init
firebase deploy


# book types
Fiction
This category includes narratives created from the author's imagination. Examples: novels, short stories, and plays.
Nonfiction
These books provide factual information or recount real events. Examples: biographies, memoirs, and essays.
Poetry
A literary form that uses rhythmic and aesthetic qualities of language to evoke meanings. Examples: anthologies of poems or individual collections by poets.
Fantasy
A genre that includes magical elements and fantastical worlds. Examples: "The Hobbit" by J.R.R. Tolkien and "Harry Potter" series by J.K. Rowling.
Mystery/Thriller
These books focus on suspenseful plots involving crime or investigation. Examples: "Gone Girl" by Gillian Flynn and "The Girl with the Dragon Tattoo" by Stieg Larsson.
Historical Fiction
A genre that reconstructs past events through fictional narratives, often featuring real historical figures or events. Examples: "The Book Thief" by Markus Zusak and "All the Light We Cannot See" by Anthony Doerr.


# Prompt

Create a JSON list for me, with books.
Title, author, publisher, publish year, publish date, ISBN.
Add a list for genres, booktype (fiction, non-fiction, poetry etc.)
Locations are very important. If a book deals with multiple locations, include all of them under the locations key.
Also, provide the latitude and longitude of each location.

Example:

    {
        "title": "The Great Railway Bazaar",
        "author": "Paul Theroux",
        "description": "A vivid travelogue documenting Theroux's journey by train across Europe, Asia, and the Middle East.",
        "booktype": "Nonfiction",
        "publicationDate": "1975-01-01",
        "genre": "Travel",
        "rating": 4.1,
        "pageCount": 400,
        "isbn": "9780141189147",
        "language": "English",
        "publisher": "Houghton Mifflin",
        "tags": ["Train", "Asia", "Adventure"],
        "locations": [
            {
                "city": "Istanbul",
                "latitude": 41.0082,
                "longitude": 28.9784,
                "description": "A key stop on Theroux's journey, bridging Europe and Asia."
            },
            {
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "description": "A major station on the rail journey through India."
            },
            {
                "city": "Kyoto",
                "latitude": 35.0116,
                "longitude": 135.7681,
                "description": "A memorable destination in Japan on the journey."
            },
             {
                "city": "Mangalore",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.9141,
        "lng": 74.8560,
        "in_book": "Chapter 5",
        "description": "The author explores Mangalore's food scene, experiencing both disappointing tourist traps and delicious home-cooked meals, and learns about the Tamil fishing community's presence in the region."
          },
        ]
    },


Desired output: JSON structure.

I would now like to give you the name of a book and its author. if you know attributes of this book, please create a JSON structure (format mentioned above) for me. Don't make up stuff!

Ready?


Locations are very important. If a book deals with multiple locations, make a separate entry for each one of them under the locations key.
Also, don't forget to provide the latitude and longitude of each location.

Example: ==================
     {
        "city": "Mangalore",
        "state": "Karnataka",
        "country": "India",
        "lat": 12.9141,
        "lng": 74.8560,
        "in_book": "Chapter 5",
        "description": "The author explores Mangalore's food scene, experiencing both disappointing tourist traps and delicious home-cooked meals, and learns about the Tamil fishing community's presence in the region."
      },

Ready?




I have uploaded pdf of books.
I might specify a particular chapter. and you will review the chapter, find all the places (locations mentioned in that chapter) and for each "place"
Create the following: City, state, country (if known), lat, lng, in_book (chapter number), description (what role the place plays in the book)

So I will ask for a few books, and you have to generate the book JSONs... are you ready?


If you know of famous books that deal with {country:Iceland} please create the JSON.


