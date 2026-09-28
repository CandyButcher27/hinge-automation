import { z } from "zod";
import { now } from "../db/database.js";
import { defineTool } from "./registry.js";
import { readProfile } from "./profile.js";
import { readPreferences } from "./preferences.js";
import type { Conversation, Draft } from "../types/index.js";

export const addConversation = defineTool({
  name: "add_conversation",
  description:
    "Store conversation text the user has manually pasted in. Never reads messages from any dating service.",
  inputSchema: {
    profile_id: z.number().int().positive(),
    content: z.string().min(1).max(100000),
  },
  handler: (db, args) => {
    if (!readProfile(db, args.profile_id)) {
      return { error: "profile_not_found", profile_id: args.profile_id };
    }
    const info = db
      .prepare(
        `INSERT INTO conversations (profile_id, content, created_at) VALUES (?, ?, ?)`,
      )
      .run(args.profile_id, args.content, now());
    return { conversation_id: Number(info.lastInsertRowid), status: "created" };
  },
});

export function readConversations(db: any, profileId: number): Conversation[] {
  return db
    .prepare(`SELECT * FROM conversations WHERE profile_id = ? ORDER BY id`)
    .all(profileId) as Conversation[];
}

export const getConversation = defineTool({
  name: "get_conversation",
  description: "Return the conversation entries the user supplied for a profile.",
  inputSchema: { profile_id: z.number().int().positive() },
  handler: (db, args) => {
    if (!readProfile(db, args.profile_id)) {
      return { error: "profile_not_found", profile_id: args.profile_id };
    }
    const rows = readConversations(db, args.profile_id);
    return { count: rows.length, conversations: rows };
  },
});

export const draftReply = defineTool({
  name: "draft_reply",
  description:
    "Return the context Claude needs to write a reply draft: the profile, the user's preferences, and the conversation so far. Produces a draft only - it never sends anything anywhere. The user copies the text and sends it themselves.",
  inputSchema: {
    profile_id: z.number().int().positive(),
    objective: z.string().max(500).optional(),
    tone: z.string().max(200).optional(),
  },
  handler: (db, args) => {
    const profile = readProfile(db, args.profile_id);
    if (!profile) {
      return { error: "profile_not_found", profile_id: args.profile_id };
    }
    const conversations = readConversations(db, args.profile_id);
    return {
      profile,
      preferences: readPreferences(db),
      conversations,
      objective: args.objective ?? "respond naturally",
      tone: args.tone ?? null,
      delivery: "manual",
      instructions:
        "Write one or two candidate replies. Do not send them. The user will copy the text and send it manually.",
      uncertainties: conversations.length
        ? []
        : ["No conversation has been supplied for this profile yet."],
    };
  },
});

export const saveDraft = defineTool({
  name: "save_draft",
  description: "Save a message draft locally for the user to copy later.",
  inputSchema: {
    profile_id: z.number().int().positive().optional(),
    draft: z.string().min(1).max(20000),
  },
  handler: (db, args) => {
    if (args.profile_id !== undefined && !readProfile(db, args.profile_id)) {
      return { error: "profile_not_found", profile_id: args.profile_id };
    }
    const info = db
      .prepare(
        `INSERT INTO drafts (profile_id, draft, status, created_at) VALUES (?, ?, 'draft', ?)`,
      )
      .run(args.profile_id ?? null, args.draft, now());
    return { draft_id: Number(info.lastInsertRowid), status: "draft" };
  },
});

export function readDrafts(db: any, profileId?: number): Draft[] {
  if (profileId === undefined) {
    return db.prepare(`SELECT * FROM drafts ORDER BY id DESC`).all() as Draft[];
  }
  return db
    .prepare(`SELECT * FROM drafts WHERE profile_id = ? ORDER BY id DESC`)
    .all(profileId) as Draft[];
}

export const listDrafts = defineTool({
  name: "list_drafts",
  description: "List saved drafts, optionally filtered to one profile.",
  inputSchema: { profile_id: z.number().int().positive().optional() },
  handler: (db, args) => {
    const rows = readDrafts(db, args.profile_id);
    return { count: rows.length, drafts: rows };
  },
});

export const messageTools = [
  addConversation,
  getConversation,
  draftReply,
  saveDraft,
  listDrafts,
];
