import gplay from 'google-play-scraper';
import { Database } from './db.js';
import logger from './logger.js';
import cliProgress from 'cli-progress';

const bar1 = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
const maxCallsPerSecond = 25;

function getCurrentDate() {
    const date = new Date();
    return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}

const db = new Database(`${getCurrentDate()}.db`);
db.createInfoTable();

(async () => {
    const apps = await db.getAppsNotInInfo();
    bar1.start(apps.length, 0);
    const packageNames = apps.map(app => app.package);
    console.log(packageNames.length);
    await queryAppInfo(packageNames);
    bar1.stop();
})();

async function queryAppInfo(packageNames) {
    const queue = [];
    const processQueue = () => {
      const tasksToProcess = queue.splice(0, maxCallsPerSecond);
      tasksToProcess.forEach(task => task());
    }
    const intervalId = setInterval(processQueue, 1000);
  
    for (let packageName of packageNames) {
        queue.push(async () => {
            try {
                let result = await gplay.app({
                    appId: packageName,
                    lang: 'en',
                    country: 'at'
                });
                await save(packageName, result);
            } catch (error) {
                logger.error(`Failed to fetch ${error} `);
            }
        });
    }
    while (queue.length > 0) {
        bar1.update(packageNames.length - queue.length);
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    clearInterval(intervalId);
}

async function save(packageName, result) {
    let installs = result.installs;
    let minInstalls = result.minInstalls;
    let maxInstalls = result.maxInstalls;
    let free = result.free;
    let json = JSON.stringify(result);
    await db.savePackageInfo(packageName, installs, minInstalls, maxInstalls, free, json)
}