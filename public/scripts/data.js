// data.js


window.locations = [
    {
        "city": "New Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "books": [
            {
                "title": "City of Djinns",
                "author": "William Dalrymple",
                "description": "A travelogue exploring the ancient history and modern life of New Delhi.",
                "booktype": "Travel Book",
                "publicationDate": "1993-01-01",
                "genre": "Non-fiction",
                "rating": 4.6,
                "pageCount": 352,
                "isbn": "9780142001004"
            },
            {
                "title": "The White Tiger",
                "author": "Aravind Adiga",
                "description": "A dark and humorous novel about India's class struggle.",
                "booktype": "Fiction",
                "publicationDate": "2008-04-22",
                "genre": "Literary Fiction",
                "rating": 4.2,
                "pageCount": 304,
                "isbn": "9781416562603"
            },
            {
                "title": "Delhi: A Novel",
                "author": "Khushwant Singh",
                "description": "A sweeping novel exploring the history and people of Delhi over centuries.",
                "booktype": "Fiction",
                "publicationDate": "1990-09-20",
                "genre": "Historical Fiction",
                "rating": 4.0,
                "pageCount": 392,
                "isbn": "9780140126198"
            }
        ],
        "createdAt": "2024-09-01T12:00:00Z"
    },
    {
        "city": "Mumbai",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "books": [
            {
                "title": "Shantaram",
                "author": "Gregory David Roberts",
                "description": "An epic novel about an Australian fugitive who finds himself drawn into the underworld of Mumbai.",
                "booktype": "Fiction",
                "publicationDate": "2003-09-01",
                "genre": "Adventure",
                "rating": 4.4,
                "pageCount": 936,
                "isbn": "9780312330538"
            },
            {
                "title": "Maximum City: Bombay Lost and Found",
                "author": "Suketu Mehta",
                "description": "A memoir and exploration of the complex, chaotic, and beautiful city of Mumbai.",
                "booktype": "Non-fiction",
                "publicationDate": "2004-09-30",
                "genre": "Memoir",
                "rating": 4.3,
                "pageCount": 560,
                "isbn": "9780375703409"
            },
            {
                "title": "The Moor's Last Sigh",
                "author": "Salman Rushdie",
                "description": "A multi-generational family saga set in the spice trade of Mumbai.",
                "booktype": "Fiction",
                "publicationDate": "1995-09-25",
                "genre": "Magical Realism",
                "rating": 4.1,
                "pageCount": 448,
                "isbn": "9780679744665"
            }
        ],
        "createdAt": "2024-09-01T12:00:00Z"
    },
    {
        "city": "Kolkata",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "books": [
            {
                "title": "The Shadow Lines",
                "author": "Amitav Ghosh",
                "description": "A novel about memories, borders, and the ties between India and Bangladesh.",
                "booktype": "Fiction",
                "publicationDate": "1988-11-15",
                "genre": "Historical Fiction",
                "rating": 4.5,
                "pageCount": 288,
                "isbn": "9780618329960"
            },
            {
                "title": "City of Joy",
                "author": "Dominique Lapierre",
                "description": "A non-fiction work chronicling the struggles and resilience of the people in the slums of Kolkata.",
                "booktype": "Non-fiction",
                "publicationDate": "1985-01-01",
                "genre": "History",
                "rating": 4.7,
                "pageCount": 400,
                "isbn": "9780449208957"
            },
            {
                "title": "The Hungry Tide",
                "author": "Amitav Ghosh",
                "description": "A novel set in the Sundarbans, focusing on the clash between nature, culture, and survival.",
                "booktype": "Fiction",
                "publicationDate": "2004-05-15",
                "genre": "Environmental Fiction",
                "rating": 4.3,
                "pageCount": 333,
                "isbn": "9780618329977"
            }
        ],
        "createdAt": "2024-09-01T12:00:00Z"
    },
    {
        "city": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "books": [
            {
                "title": "The Red Carpet",
                "author": "Lavanya Sankaran",
                "description": "A collection of short stories offering a vivid portrayal of life in modern Bengaluru.",
                "booktype": "Fiction",
                "publicationDate": "2005-04-12",
                "genre": "Short Stories",
                "rating": 4.0,
                "pageCount": 240,
                "isbn": "9780385338306"
            },
            {
                "title": "Bangalore: Roots and Beyond",
                "author": "Peter Colaco",
                "description": "A history of Bengaluru, examining its transformation from a sleepy town to a tech hub.",
                "booktype": "Non-fiction",
                "publicationDate": "1997-01-01",
                "genre": "History",
                "rating": 4.4,
                "pageCount": 320,
                "isbn": "9788170995780"
            }
        ],
        "createdAt": "2024-09-01T12:00:00Z"
    },
    {
        "city": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "books": [
            {
                "title": "The House of Blue Mangoes",
                "author": "David Davidar",
                "description": "A multi-generational saga set in Tamil Nadu, chronicling the struggles of a family in British-ruled India.",
                "booktype": "Fiction",
                "publicationDate": "2002-05-28",
                "genre": "Historical Fiction",
                "rating": 4.2,
                "pageCount": 384,
                "isbn": "9780066212640"
            },
            {
                "title": "Tamarind City: Where Modern India Began",
                "author": "Bishwanath Ghosh",
                "description": "A travelogue that captures the essence of Chennai and its transformation over time.",
                "booktype": "Non-fiction",
                "publicationDate": "2012-01-15",
                "genre": "Travel Book",
                "rating": 4.3,
                "pageCount": 264,
                "isbn": "9789350292433"
            }
        ],
        "createdAt": "2024-09-01T12:00:00Z"
    }
];


window.booklist = [
    {
        "title": "Tale of Two Cities",
        "author": "Charles Dickens",
        "description": "A historical novel set before and during the French Revolution, exploring themes of justice, sacrifice, and love.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "London",
                "lat": 51.5074,
                "lng": -0.1278
            },
            {
                "city": "Paris",
                "lat": 48.8566,
                "lng": 2.3522
            }
        ]
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "A portrayal of the American Dream, wealth, and class divisions during the Roaring Twenties in the U.S.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "New York",
                "lat": 40.7128,
                "lng": -74.0060
            }
        ]
    },
    {
        "title": "Les Misérables",
        "author": "Victor Hugo",
        "description": "A story of injustice, redemption, and revolution in post-revolutionary France, centered on the struggles of ex-convict Jean Valjean.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Paris",
                "lat": 48.8566,
                "lng": 2.3522
            }
        ]
    },
    {
        "title": "The Big Sleep",
        "author": "Raymond Chandler",
        "description": "A noir detective novel featuring Philip Marlowe, filled with intrigue, corruption, and mystery in 1930s Los Angeles.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Los Angeles",
                "lat": 34.0522,
                "lng": -118.2437
            }
        ]
    },
    {
        "title": "Wild Swans",
        "author": "Jung Chang",
        "description": "A family memoir that spans three generations of Chinese women living through the upheavals of 20th-century China.",
        "booktype": "Non-Fiction",
        "locations": [
            {
                "city": "Beijing",
                "lat": 39.9042,
                "lng": 116.4074
            }
        ]
    },
    {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "description": "A psychological novel about morality, guilt, and redemption, following the struggles of a man who commits murder.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Saint Petersburg",
                "lat": 55.7558,
                "lng": 37.6176
            }
        ]
    },
    {
        "title": "Norwegian Wood",
        "author": "Haruki Murakami",
        "description": "A nostalgic and emotional novel about love, loss, and coming of age in 1960s Japan.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Tokyo",
                "lat": 35.6895,
                "lng": 139.6917
            }
        ]
    },
    {
        "title": "The Power of One",
        "author": "Bryce Courtenay",
        "description": "A story of a young boy’s journey to adulthood in South Africa, against the backdrop of apartheid and boxing.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Johannesburg",
                "lat": -33.8688,
                "lng": 151.2093
            }
        ]
    },
    {
        "title": "The Posthumous Memoirs of Brás Cubas",
        "author": "Machado de Assis",
        "description": "A witty and satirical narrative about life, death, and the absurdity of society, told by a dead narrator.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Rio de Janeiro",
                "lat": -22.9068,
                "lng": -43.1729
            }
        ]
    },
    {
        "title": "The Betrothed",
        "author": "Alessandro Manzoni",
        "description": "A historical novel set in 17th-century Italy, dealing with love, faith, and struggles against tyranny.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Milan",
                "lat": 45.4654,
                "lng": 9.1859
            }
        ]
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "description": "A classic novel about teenage alienation and rebellion, following Holden Caulfield's journey through New York.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "New York",
                "lat": 40.7306,
                "lng": -73.9352
            }
        ]
    },
    {
        "title": "Shantaram",
        "author": "Gregory David Roberts",
        "description": "A semi-autobiographical novel about an Australian fugitive who finds a new life in the slums of Mumbai.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Mumbai",
                "lat": 19.0760,
                "lng": 72.8777
            }
        ]
    },
    {
        "title": "Dubliners",
        "author": "James Joyce",
        "description": "A collection of short stories depicting life, love, and loss in early 20th-century Dublin.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Dublin",
                "lat": 53.3498,
                "lng": -6.2603
            }
        ]
    },
    {
        "title": "On the Road",
        "author": "Jack Kerouac",
        "description": "A seminal work of the Beat Generation, chronicling the adventures of Sal Paradise and Dean Moriarty across America.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "San Francisco",
                "lat": 37.7749,
                "lng": -122.4194
            }
        ]
    },
    {
        "title": "Philadelphia Fire",
        "author": "John Edgar Wideman",
        "description": "A novel based on the 1985 bombing of the MOVE headquarters, exploring racial tensions in Philadelphia.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Philadelphia",
                "lat": 39.9526,
                "lng": -75.1652
            }
        ]
    },
    {
        "title": "The Reader",
        "author": "Bernhard Schlink",
        "description": "A novel about the relationship between a young boy and an older woman, set against the backdrop of post-WWII Germany.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Hamburg",
                "lat": 53.5511,
                "lng": 9.9937
            }
        ]
    },
    {
        "title": "Don Quixote",
        "author": "Miguel de Cervantes",
        "description": "A classic tale of a man who believes himself to be a knight, tilting at windmills and chasing adventures.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Madrid",
                "lat": 40.4168,
                "lng": -3.7038
            }
        ]
    },
    {
        "title": "The Orenda",
        "author": "Joseph Boyden",
        "description": "A historical novel about the clash between Native Americans and European settlers in 17th-century Canada.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Ottawa",
                "lat": 45.4215,
                "lng": -75.6972
            }
        ]
    },
    {
        "title": "Smilla's Sense of Snow",
        "author": "Peter Høeg",
        "description": "A literary thriller about Smilla, a Greenlandic woman investigating the death of a young boy in Copenhagen.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Copenhagen",
                "lat": 55.6761,
                "lng": 12.5683
            }
        ]
    },
    {
        "title": "The Diary of a Young Girl",
        "author": "Anne Frank",
        "description": "The poignant diary of a Jewish girl hiding from the Nazis in occupied Amsterdam during WWII.",
        "booktype": "Non-Fiction",
        "locations": [
            {
                "city": "Amsterdam",
                "lat": 52.3676,
                "lng": 4.9041
            }
        ]
    },
    {
        "title": "The Amazing Adventures of Kavalier & Clay",
        "author": "Michael Chabon",
        "description": "A novel about two Jewish cousins creating a comic book empire during the Golden Age of comics in the 1930s and 1940s.",
        "booktype": "Fiction",
        "locations": [
            {
                "city": "Minneapolis",
                "lat": 45.0382,
                "lng": -93.2858
            }
        ]
    }
]




// Array of locations with book details
old_books = [
    {
        lat: 51.5074,
        lng: -0.1278,
        title: "Tale of Two Cities",
        author: "Charles Dickens",
        description: "Set in London and Paris.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 40.7128,
        lng: -74.0060,
        title: "The Great Gatsby",
        author: "F. Scott Fitzgerald",
        description: "Set in New York.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },

    {
        lat: 48.8566,
        lng: 2.3522,
        title: "Les Misérables",
        author: "Victor Hugo",
        description: "Set in Paris, France.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 34.0522,
        lng: -118.2437,
        title: "The Big Sleep",
        author: "Raymond Chandler",
        description: "Set in Los Angeles, USA.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 39.9042,
        lng: 116.4074,
        title: "Wild Swans",
        author: "Jung Chang",
        description: "Set in Beijing, China.",
        image: "link_to_image.jpg",
        booktype: "Non-Fiction"
    },
    {
        lat: 55.7558,
        lng: 37.6176,
        title: "Crime and Punishment",
        author: "Fyodor Dostoevsky",
        description: "Set in Saint Petersburg, Russia.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 35.6895,
        lng: 139.6917,
        title: "Norwegian Wood",
        author: "Haruki Murakami",
        description: "Set in Tokyo, Japan.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: -33.8688,
        lng: 151.2093,
        title: "The Power of One",
        author: "Bryce Courtenay",
        description: "Set in Johannesburg, South Africa.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: -22.9068,
        lng: -43.1729,
        title: "The Posthumous Memoirs of Brás Cubas",
        author: "Machado de Assis",
        description: "Set in Rio de Janeiro, Brazil.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 45.4654,
        lng: 9.1859,
        title: "The Betrothed",
        author: "Alessandro Manzoni",
        description: "Set in Milan, Italy.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 40.7306,
        lng: -73.9352,
        title: "The Catcher in the Rye",
        author: "J.D. Salinger",
        description: "Set in New York City, USA.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 19.0760,
        lng: 72.8777,
        title: "Shantaram",
        author: "Gregory David Roberts",
        description: "Set in Mumbai, India.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 53.3498,
        lng: -6.2603,
        title: "Dubliners",
        author: "James Joyce",
        description: "Set in Dublin, Ireland.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 37.7749,
        lng: -122.4194,
        title: "On the Road",
        author: "Jack Kerouac",
        description: "Set in San Francisco, USA.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 39.9526,
        lng: -75.1652,
        title: "Philadelphia Fire",
        author: "John Edgar Wideman",
        description: "Set in Philadelphia, USA.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 53.5511,
        lng: 9.9937,
        title: "The Reader",
        author: "Bernhard Schlink",
        description: "Set in Hamburg, Germany.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 40.4168,
        lng: -3.7038,
        title: "Don Quixote",
        author: "Miguel de Cervantes",
        description: "Set in Madrid, Spain.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 45.4215,
        lng: -75.6972,
        title: "The Orenda",
        author: "Joseph Boyden",
        description: "Set in Ottawa, Canada.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 55.6761,
        lng: 12.5683,
        title: "Smilla's Sense of Snow",
        author: "Peter Høeg",
        description: "Set in Copenhagen, Denmark.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 59.4370,
        lng: 24.7535,
        title: "The Inspector and the Saint",
        author: "Martin Cruz Smith",
        description: "Set in Tallinn, Estonia.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 52.3676,
        lng: 4.9041,
        title: "The Diary of a Young Girl",
        author: "Anne Frank",
        description: "Set in Amsterdam, Netherlands.",
        image: "link_to_image.jpg",
        booktype: "Non-Fiction"
    },
    {
        lat: 45.0382,
        lng: -93.2858,
        title: "The Amazing Adventures of Kavalier & Clay",
        author: "Michael Chabon",
        description: "Set in Minneapolis, USA.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    },
    {
        lat: 55.6761,
        lng: 12.5683,
        title: "Miss Smilla's Feeling for Snow",
        author: "Peter Høeg",
        description: "Set in Copenhagen, Denmark.",
        image: "link_to_image.jpg",
        booktype: "Fiction"
    }
];
