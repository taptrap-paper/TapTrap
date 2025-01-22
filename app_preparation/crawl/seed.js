//var gplay = require('google-play-scraper').memoized({ maxAge: 1000 * 60 * 5 }); // 5 minutes cache 
import { Database } from './db.js';
import gplay from 'google-play-scraper';
import logger from './logger.js';

let categories = gplay.category;
let collections = gplay.collection;

function getCurrentDate() {
  const date = new Date();
  return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}

const db = new Database(`${getCurrentDate()}.db`);

(async () => {
  logger.info("Starting crawl");
  await db.createTable();
  await getSeedApps();
  logger.info("Retrieved seed apps");
})();

async function getSeedApps() {
  for (let category in categories) {
    for (let collection in collections) {
        try {
          let result = await gplay.list({
            category: categories[category],
            collection: collections[collection],
            num: 200, // the maximum seems to be set to 200 here
            lang: "en",
            country: "at",
            fullDetail: false,
            throttle: 10 // 10 requests per second
          });
          db.savePackages(result);
        } catch (error) {
          logger.error(`Failed to fetch ${error} `);
        }
      };
  }
}