import { z } from "zod";
import { now } from "../db/database.js";
import { defineTool } from "./registry.js";
import type { Profile } from "../types/index.js";

export const addProfileInput = {
  name: z.string().min(1).max(200).optional(),
  age: z.number().int().min(18).max(120).optional(),
  occupation: z.string().max(200).optional(),
  location: z.string().max(200).optional(),
  bio: z.string().max(20000).optional(),
  notes: z.string().max(20000).optional(),
};

export const addProfile = defineTool({
  name: "add_profile",
  description:
    "Store a profile the user has manually typed or pasted in. Never fetches, scrapes or imports from any dating service.",
  inputSchema: addProfileInput,
  handler: (db, args) => {
    const ts = now();
    const stmt = db.prepare(
      `INSERT INTO profiles (name, age, occupation, location, bio, notes, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    );
    const info = stmt.run(
      args.name ?? null,
      args.age ?? null,
      args.occupation ?? null,
      args.location ?? null,
      args.bio ?? null,
      args.notes ?? null,
      ts,
      ts,
    );
    return { profile_id: Number(info.lastInsertRowid), status: "created" };
  },
});

export function readProfile(db: any, profileId: number): Profile | undefined {
  return db.prepare(`SELECT * FROM profiles WHERE id = ?`).get(profileId) as
    | Profile
    | undefined;
}

export const getProfile = defineTool({
  name: "get_profile",
  description: "Return one locally stored profile by id.",
  inputSchema: { profile_id: z.number().int().positive() },
  handler: (db, args) => {
    const profile = readProfile(db, args.profile_id);
    if (!profile) {
      return { error: "not_found", profile_id: args.profile_id };
    }
    return { profile };
  },
});

export const listProfiles = defineTool({
  name: "list_profiles",
  description: "List locally stored profiles, newest first.",
  inputSchema: { limit: z.number().int().min(1).max(200).optional() },
  handler: (db, args) => {
    const rows = db
      .prepare(`SELECT * FROM profiles ORDER BY id DESC LIMIT ?`)
      .all(args.limit ?? 50) as unknown as Profile[];
    return { count: rows.length, profiles: rows };
  },
});

export const profileTools = [addProfile, getProfile, listProfiles];
