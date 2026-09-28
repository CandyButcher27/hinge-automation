import { DatabaseSync } from "node:sqlite";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { SCHEMA } from "./schema.js";

export function defaultDbPath(): string {
  if (process.env.DATING_ASSISTANT_DB) return process.env.DATING_ASSISTANT_DB;
  const here = dirname(fileURLToPath(import.meta.url));
  return join(here, "..", "..", "data", "assistant.db");
}

export function openDb(path: string = defaultDbPath()): DatabaseSync {
  if (path !== ":memory:") mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec(SCHEMA);
  return db;
}

export function now(): string {
  return new Date().toISOString();
}
