// node scripts/fetch_travel_openlibrary_inspect_all.mjs
// Fetch the first 20 "travel" works and print EVERY field for each work.

const LIMIT = 20;           // change as needed (Open Library allows larger values)
const DETAILS = true;       // include extra fields when available

const fetchJson = async (url) => (await fetch(url)).json();

async function run() {
  const url = `https://openlibrary.org/subjects/travel.json?limit=${LIMIT}&details=${DETAILS}`;
  console.log(`Fetching: ${url}\n`);

  const data = await fetchJson(url);

  if (!Array.isArray(data.works)) {
    console.error("No 'works' array in response. Full payload below:");
    console.dir(data, { depth: null, maxArrayLength: null });
    return;
  }

  console.log(`Retrieved ${data.works.length} works. Printing all fields per work:\n`);

  data.works.forEach((work, i) => {
    console.log(`\n==================== WORK ${i + 1} ====================\n`);
    // Print the entire object with all nested fields
    console.dir(work, { depth: null, maxArrayLength: null });
  });

  // Optional: also dump the entire works array as pretty JSON to a file
  // Uncomment to save:
  // const fs = await import('node:fs/promises');
  // await fs.mkdir('bulk', { recursive: true });
  // await fs.writeFile('bulk/travel_works_raw.json', JSON.stringify(data.works, null, 2));
  // console.log('\nSaved full works JSON to bulk/travel_works_raw.json');
}

run().catch(err => {
  console.error('Error:', err);
});
