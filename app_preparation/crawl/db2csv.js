import { Database } from './db.js';
import fs from 'fs';

function getCurrentDate() {
    const date = new Date();
    return `${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}`;
}
const db = new Database(`${getCurrentDate()}.db`);

(async () => {
    const apps = await db.getAppsFreeAtLeast(0);
    const pids = apps.map(app => app.package);
    // life after line add pids to a csv file
    fs.writeFileSync(`${getCurrentDate()}-free.csv`, pids.join('\n'));
})();