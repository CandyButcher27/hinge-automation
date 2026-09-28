import { z } from "zod";
import { defineTool } from "./registry.js";
import { readProfile } from "./profile.js";
import { readPreferences } from "./preferences.js";
import { readConversations } from "./messages.js";
import type { Profile } from "../types/index.js";

const INTEREST_LEAD = /\b(?:likes?|loves?|enjoys?|into|obsessed with|passionate about)\b/i;

export function extractInterests(text: string): string[] {
  const found = new Set<string>();
  for (const sentence of splitSentences(text)) {
    const lead = sentence.match(INTEREST_LEAD);
    if (!lead) continue;
    const tail = sentence.slice((lead.index ?? 0) + lead[0].length);
    for (const part of tail.split(/,| and | & /i)) {
      const cleaned = part.replace(/[^\p{L}\p{N}\s'-]/gu, " ").trim();
      if (cleaned && cleaned.split(/\s+/).length <= 4) found.add(cleaned.toLowerCase());
    }
  }
  return [...found];
}

export function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function extractTopics(profile: Profile): string[] {
  const topics: string[] = [];
  const bio = profile.bio ?? "";
  for (const quoted of bio.match(/"[^"]{3,200}"/g) ?? []) {
    topics.push(quoted.slice(1, -1).trim());
  }
  for (const sentence of splitSentences(bio)) {
    if (sentence.length >= 15 && !topics.includes(sentence)) topics.push(sentence);
  }
  if (profile.occupation) topics.push(`their work as ${profile.occupation}`);
  if (profile.location) topics.push(`things to do in ${profile.location}`);
  return topics.slice(0, 12);
}

function missingFields(profile: Profile): string[] {
  const gaps: string[] = [];
  for (const field of ["name", "age", "occupation", "location", "bio"] as const) {
    if (!profile[field]) gaps.push(`no ${field} recorded`);
  }
  return gaps;
}

export const analyzeProfile = defineTool({
  name: "analyze_profile",
  description:
    "Return structured raw material about a stored profile - possible interests, conversation topics, open questions, preference overlaps and gaps. It does not judge or decide; Claude and the user do the reasoning.",
  inputSchema: { profile_id: z.number().int().positive() },
  handler: (db, args) => {
    const profile = readProfile(db, args.profile_id);
    if (!profile) {
      return { error: "profile_not_found", profile_id: args.profile_id };
    }
    const text = [profile.bio, profile.notes].filter(Boolean).join("\n");
    const preferences = readPreferences(db);
    const haystack = text.toLowerCase();

    const potential_compatibility = preferences
      .filter((p) =>
        p.value
          .toLowerCase()
          .split(/,|;|\n/)
          .map((v) => v.trim())
          .some((v) => v.length > 2 && haystack.includes(v)),
      )
      .map((p) => `${p.category}: overlaps with something in the profile text`);

    const conversations = readConversations(db, args.profile_id);
    const uncertainties = missingFields(profile);
    if (!preferences.length) {
      uncertainties.push("no user preferences saved, so overlap cannot be checked");
    }
    if (!conversations.length) {
      uncertainties.push("no conversation supplied for this profile");
    }

    return {
      profile,
      possible_interests: extractInterests(text),
      conversation_topics: extractTopics(profile),
      questions_to_consider: [
        "Which detail here is the strongest opener hook, and why?",
        "Does anything here conflict with the user's saved deal breakers?",
        "What is still unknown that would change the user's decision?",
      ],
      potential_compatibility,
      uncertainties,
      note: "Extraction is a plain text heuristic. It is not a compatibility score and makes no recommendation.",
    };
  },
});

export const analysisTools = [analyzeProfile];
