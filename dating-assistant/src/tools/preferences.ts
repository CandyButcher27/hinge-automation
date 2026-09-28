import { z } from "zod";
import { now } from "../db/database.js";
import { defineTool } from "./registry.js";
import type { Preference } from "../types/index.js";

export const setPreference = defineTool({
  name: "set_preference",
  description:
    "Save or update one of the user's own dating preferences, e.g. communication style, interests, deal breakers, relationship goals.",
  inputSchema: {
    category: z.string().min(1).max(100),
    value: z.string().min(1).max(5000),
  },
  handler: (db, args) => {
    const ts = now();
    db.prepare(
      `INSERT INTO preferences (category, value, created_at, updated_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(category) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at`,
    ).run(args.category, args.value, ts, ts);
    const row = db
      .prepare(`SELECT * FROM preferences WHERE category = ?`)
      .get(args.category) as unknown as Preference;
    return { preference_id: row.id, status: "saved", category: row.category };
  },
});

export function readPreferences(db: any): Preference[] {
  return db
    .prepare(`SELECT * FROM preferences ORDER BY category`)
    .all() as Preference[];
}

export const getPreferences = defineTool({
  name: "get_preferences",
  description: "Return all saved user preferences.",
  inputSchema: {},
  handler: (db) => {
    const rows = readPreferences(db);
    return { count: rows.length, preferences: rows };
  },
});

export const preferenceTools = [setPreference, getPreferences];
