import pino from 'pino';
import pkg from 'pino-multi-stream';
const { multistream } = pkg;
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const date = new Date();


const logFilename = path.join(
    __dirname,
    `log-${date.getDate()}-${date.getMonth() + 1}-${date.getFullYear()}.log`
  );
const fileStream = fs.createWriteStream(logFilename, { flags: 'a' });

const streams = [
    { stream: process.stdout },   // Log to the console
    { stream: fileStream }        // Log to the file
  ];

  const logger = pino(
    { level: 'info'},
    multistream(streams)
  );  

export default logger;