import test from "node:test";
import assert from "node:assert/strict";
import { openDb } from "./db/database.js";
import { callTool } from "./server.js";
import { extractInterests, splitSentences } from "./tools/analysis.js";

test("extractInterests pulls phrases from like/love clauses", () => {
  const found = extractInterests("Likes hiking, coffee and photography. Into bouldering.");
  assert.deepEqual(found.sort(), ["bouldering", "coffee", "hiking", "photography"]);
  assert.deepEqual(extractInterests("Software engineer in Boston."), []);
});

test("splitSentences splits on punctuation and newlines", () => {
  assert.deepEqual(splitSentences("One. Two!\nThree"), ["One.", "Two!", "Three"]);
});

test("analyze_profile surfaces material without deciding", () => {
  const d = openDb(":memory:");
  const { profile_id } = callTool(d, "add_profile", {
    name: "Sam",
    age: 24,
    occupation: "Software engineer",
    bio: 'Likes hiking, coffee and photography.\n"My simple pleasures..." "Finding a new coffee shop and spending three hours there."',
  }) as any;
  callTool(d, "set_preference", { category: "interests", value: "coffee, climbing" });

  const out = callTool(d, "analyze_profile", { profile_id }) as any;
  assert.ok(out.possible_interests.includes("coffee"));
  assert.ok(out.conversation_topics.some((t: string) => t.includes("coffee shop")));
  assert.ok(out.potential_compatibility.some((c: string) => c.startsWith("interests")));
  assert.ok(out.uncertainties.includes("no location recorded"));
  assert.ok(out.uncertainties.includes("no conversation supplied for this profile"));
  assert.ok(out.questions_to_consider.length > 0);
  assert.equal(out.profile.name, "Sam");
});
