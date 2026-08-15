Yes. I think the key realization is that **the map is a core capability of LitMap, but it should not be the homepage's only mental model**.

Right now, it sounds like we're starting with:

> "Here is the map. What would you like to do with it?"

I would flip that around:

> **"What kind of book discovery are you in the mood for?"**

The map then becomes one of the most powerful ways to answer that question.

### 1. Start by identifying the major discovery journeys

I see at least these:

| User arrives thinking...                    | LitMap should offer...                                |
| ------------------------------------------- | ----------------------------------------------------- |
| "I'm going to Kenya."                       | **Explore books about / set in / connected to Kenya** |
| "I'm going to Barcelona."                   | **Discover Barcelona through books**                  |
| "I want to travel somewhere through books." | **Explore the world on the map**                      |
| "I loved this book."                        | **Find similar books**                                |
| "I like this author."                       | **Discover more by / related to this author**         |
| "I want something new to read."             | **Curated discoveries**                               |
| "Show me what is interesting around here."  | **Nearby / location-based discoveries**               |
| "I remember a place from a book."           | **Explore that place and related books**              |
| "I want to browse."                         | **Wander through curated collections**                |

That last one is particularly important. **Curated discoverability** means LitMap shouldn't feel like a database that happens to have a map. It should feel like a place where the user keeps stumbling across interesting books.

### 2. The homepage could therefore have a very different hierarchy

I would envision something like:

**LitMap**

> **Discover books through places, people and stories.**

Then perhaps three prominent entry points:

**Explore the World**
A beautiful, interactive map.

**Find My Next Book**
Personalized/curated discovery.

**Explore a Place**
"Where are you curious about?"

And below that, dynamic discovery sections:

* **Places worth exploring**
* **Books you might like**
* **Author trails**
* **Recently discovered**
* **Curated collections**

The map is still visually dominant, but it isn't the entire experience.

### 3. The Bangkok example exposes an important UX principle

Suppose the map says:

> **Bangkok · 6 books**

Clicking it currently makes the six books "explode" onto the map.

That's useful **if the user's intention is geographic exploration**.

But if their intention is:

> "There are six books associated with Bangkok. What are they?"

then the correct response is probably a **place collection**.

Something like:

**Bangkok**
*6 books connected to this place*

Then six compact book cards:

* Cover
* Title
* Author
* Why it's connected to Bangkok
* Perhaps a small map/location indicator

And actions such as:

> **View on map**
> **Explore this place**

This suggests a broader principle:

**A cluster is not necessarily a visualization problem. It is potentially a discovery object.**

The cluster itself could become something meaningful.

### 4. In fact, I'd introduce the concept of "Place Pages"

Kenya shouldn't just be a region on a map.

It could become a destination page:

**Kenya**

> Discover 37 books connected to Kenya.

Then perhaps:

* **Set in Kenya**
* **About Kenya**
* **Written by Kenyan authors**
* **Travel / memoir**
* **Historical**
* **Fiction**
* **Featured discoveries**

And, of course:

**Explore Kenya on the map**

That gives LitMap a much richer information architecture.

The same model works for:

**Barcelona**
**Bangkok**
**Nairobi**
**Kerala**
**Paris**
etc.

### 5. The really interesting part: connect the discovery modes

This is where I think LitMap could become distinctive.

Imagine someone discovers a book because they're exploring **Kenya**.

They click the book.

Now LitMap says:

> **You might also like...**

But the recommendations aren't just conventional "people who liked X also liked Y."

They could be based on **relationships between books, authors and places**.

For example:

**This book → Kenya → other books about Kenya**

**This book → author → other books by this author**

**This book → Nairobi → other books set in Nairobi**

**This book → themes → similar books**

**This book → neighboring places → discover books about Tanzania**

Now the map becomes part of a **discovery graph** rather than merely a geographic visualization.

### 6. That gives us a much better definition of LitMap

I wouldn't describe it simply as:

> "A map of books."

I'd think of it more as:

> **A visual discovery engine for books, connecting books to places, authors, themes and each other.**

The map is one of the major lenses through which you explore that network.

That distinction should probably drive the entire homepage redesign.

### 7. One design question I'd like us to tackle next

Before designing the actual screen, I think we should map **the 6–8 canonical journeys through LitMap**.

For each one, we can answer:

**Entry point → user intent → first action → discovery experience → book detail → next discovery → where they can go afterward**

Then we can see what the homepage actually needs to contain.

That will prevent us from designing a beautiful homepage first and only afterward trying to invent the user journeys that fit it.
