import sqlite3 from 'sqlite3';
import logger from './logger.js';

export class Database {
    constructor(dbName) {
        this.db = new sqlite3.Database(dbName, (err) => {
            if (err) {
                logger.error('Error connecting to the SQLite database:', err.message);
            }
        });
    }

    createTable() {
        return new Promise((resolve, reject) => {
            this.db.run(`CREATE TABLE IF NOT EXISTS pids_table (
                package TEXT PRIMARY KEY,
                downloads INTEGER,
                json TEXT,
                depth INTEGER DEFAULT 0,
                similar_queried INTEGER DEFAULT 0
            )`, (err) => {
                if (err) {
                    logger.error('Error creating table:', err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    createInfoTable() {
        return new Promise((resolve, reject) => {
            this.db.run(`CREATE TABLE IF NOT EXISTS info_table (
                package TEXT PRIMARY KEY,
                installs TEXT,
                minInstalls INTEGER,
                maxInstalls INTEGER,
                free BOOLEAN,
                json TEXT
            )`, (err) => {
                if (err) {
                    logger.error('Error creating table:', err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    savePackageInfo(packageName, installs, minInstalls, maxInstalls, free, json) {
        return new Promise((resolve, reject) => {
            this.db.run(`INSERT INTO info_table (package, installs, minInstalls, maxInstalls, free, json) VALUES (?, ?, ?, ?, ?, ?)`, 
                [packageName, installs, minInstalls, maxInstalls, free, json], (err) => {
                if (err) {
                    logger.error(`Failed to save package info ${packageName} to the database:`, err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    getAppsNotInInfo() {
        // get those apps which are in pid but are not in info
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM pids_table WHERE package NOT IN (SELECT package FROM info_table)`, (err, rows) => {
                if (err) {
                    logger.error('Error fetching apps:', err.message);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }

    getAppsFreeLessThan(number) {
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM info_table WHERE maxInstalls < ? and free == 1`, [number], (err, rows) => {
                if (err) {
                    logger.error('Error fetching apps:', err.message);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }

    getAppsFreeAtLeast(number) {
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM info_table WHERE minInstalls >= ? and free == 1`, [number], (err, rows) => {
                if (err) {
                    logger.error('Error fetching apps:', err.message);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }

    // Helper method to get apps by depth and similar_queried flag
    getAppsByDepthAndFlag(depth, similarQueried) {
        return new Promise((resolve, reject) => {
            this.db.all(`SELECT * FROM pids_table WHERE depth = ? AND similar_queried = ?`, [depth, similarQueried], (err, rows) => {
                if (err) {
                    logger.error(`Failed to fetch apps with depth ${depth} and similar_queried ${similarQueried} from the database:`, err.message);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }

    // Helper method to update similar_queried flag
    updateSimilarQueried(packageId, value) {
        return new Promise((resolve, reject) => {
            this.db.run(`UPDATE pids_table SET similar_queried = ? WHERE package = ?`, [value, packageId], (err) => {
                if (err) {
                    logger.error(`Failed to update app ${packageId} with similar_queried ${value}:`, err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    // Helper method to check if an app exists
    checkIfAppExists(packageId) {
        return new Promise((resolve, reject) => {
            this.db.get(`SELECT * FROM pids_table WHERE package = ?`, [packageId], (err, row) => {
                if (err) {
                    logger.error(`Error checking if app ${packageId} exists in the database:`, err.message);
                    reject(err);
                } else {
                    resolve(!!row); // Return true if the app exists
                }
            });
        });
    }

    insertApp(app, depth, similarQueried) {
        return new Promise((resolve, reject) => {
            this.db.run(`INSERT INTO pids_table (package, downloads, json, similar_queried, depth) VALUES (?, ?, ?, ?, ?)`, 
                [app.appId, null, JSON.stringify(app), similarQueried, depth], (err) => {
                if (err) {
                    logger.error(`Failed to insert app ${app.appId} with depth ${depth} and similar_queried ${similarQueried}:`, err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    updateAppError(app, depth, errCode) {
        return new Promise((resolve, reject) => {
            this.db.run(`UPDATE pids_table SET similar_queried = ? WHERE package = ?`, [errCode, app.package], (err) => {
                if (err) {
                    logger.error(`Failed to update app ${app.package} with similar_queried ${errCode}:`, err.message);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }


    // Method to insert a user into the 'users' table
    savePackages(packageInfos) {
        const stmt = this.db.prepare(`
            INSERT OR REPLACE INTO pids_table (package, downloads, json, depth) 
            VALUES (?, ?, ?, ?)
        `);

        packageInfos.forEach(packageInfo => {
            const packageId = packageInfo.appId;  // Extract appId from the packageInfo
            const downloads = null;  // Set downloads to null (as per your note)
            const jsonString = JSON.stringify(packageInfo);  // Convert the whole object to JSON string

            // Execute the prepared statement for each package
            stmt.run([packageId, downloads, jsonString, 0], (err) => {
                if (err) {
                    logger.error(`Failed to save package ${packageId} to the database:`, err.message);
                } else {
                }
            });
        });

        stmt.finalize((err) => {
            if (err) {
                logger.error('Error finalizing statement:', err.message);
            } else {
            }
        });
        // for each packageInfo, get the appId and the whole object.
        // the downloads is NULL
        // then save it in the database
    }

    // Method to close the database connection
    close() {
        this.db.close((err) => {
            if (err) {
                logger.error('Error closing the database:', err.message);
            }
        });
    }
}
