//var gplay = require('google-play-scraper').memoized({ maxAge: 1000 * 60 * 5 }); // 5 minutes cache 
import { Database } from './db.js';
import gplay from 'google-play-scraper';
import logger from './logger.js';
import cliProgress from 'cli-progress';

const bar1 = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);

function getCurrentDate() {
  const date = new Date();
  return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}

const db = new Database(`${getCurrentDate()}.db`);

(async () => {
  logger.info("Starting crawl");
  await db.createTable();
  await bfsSimilarApps();
  logger.info("Finished BFS");
})();

let maxCallsPerSecond = 25;

// BFS method to get similar apps and store them in the database
async function bfsSimilarApps(maxDepth = 9) {
  let currentDepth = 0;

  while (currentDepth < maxDepth) {
      const appsAtCurrentDepth = await db.getAppsByDepthAndFlag(currentDepth, 0); // 0 means not yet queried. those that led to errors are ignored here
      bar1.start(appsAtCurrentDepth.length, 0);
      console.log(`Apps at depth ${currentDepth}: ${appsAtCurrentDepth.length}`);
      if (appsAtCurrentDepth.length === 0) {
        currentDepth++;
          continue; // No more apps to process at this depth
      }
          const queue = appsAtCurrentDepth.map(app => async () => {
            const similarApps = await fetchSimilarApps(app.package);
            if (similarApps == null) {
              // there was an error fetching similar apps
              await db.updateAppError(app, currentDepth, -2);
            } else {
              for (const similarApp of similarApps) {
                const exists = await db.checkIfAppExists(similarApp.appId);
                if (!exists) {
                  try {
                    await db.insertApp(similarApp, currentDepth + 1, false);
                  } catch (error) {
                    logger.error(`Failed to insert app ${similarApp.appId} with depth ${currentDepth + 1} ${error}`);
                  }
                }
              }
              await db.updateSimilarQueried(app.package, true);
            }
            bar1.increment();
          })
      for (let i = 0; i < queue.length; i += maxCallsPerSecond) {
        await Promise.all(queue.slice(i, i + maxCallsPerSecond).map(fn => fn()));
        await new Promise(resolve => setTimeout(resolve, 700)); // 1 second interval
    }
      bar1.stop();
      currentDepth++;
  }
}

async function fetchSimilarApps(packageId) {
  try {
      const result = await gplay.similar({
          appId: packageId,
          lang: "en",
          country: "at",
          fullDetail: false,
          throttle: 10
      });
      return result;
  } catch (error) {
      logger.error(`Failed to fetch similar apps for ${packageId} ${error}`);
      return null;
  }
}