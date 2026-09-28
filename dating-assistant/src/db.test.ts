import test from "node:test";
import assert from "node:assert/strict";
import { openDb } from "./db/database.js";
import { callTool } from "./server.js";

function db() {
  return openDb(":memory:");
}

test("add_profile then get_profile round-trips", () => {
  const d = db();
  const created = callTool(d, "add_profile", {
    name: "Sam",
    age: 24,
    occupation: "Software engineer",
    bio: "Likes hiking, coffee and photography.",
  }) as any;
  assert.equal(created.status, "created");
  const got = callTool(d, "get_profile", { profile_id: created.profile_id }) as any;
  assert.equal(got.profile.name, "Sam");
  assert.equal(got.profile.age, 24);
  assert.ok(got.profile.created_at);
});

test("list_profiles honours limit and returns newest first", () => {
  const d = db();
  for (const name of ["a", "b", "c"]) callTool(d, "add_profile", { name });
  const listed = callTool(d, "list_profiles", { limit: 2 }) as any;
  assert.equal(listed.count, 2);
  assert.equal(listed.profiles[0].name, "c");
});

test("missing profile id returns not_found, not a throw", () => {
  const d = db();
  assert.equal((callTool(d, "get_profile", { profile_id: 999 }) as any).error, "not_found");
  assert.equal(
    (callTool(d, "add_conversation", { profile_id: 999, content: "hi" }) as any).error,
    "profile_not_found",
  );
  assert.equal(
    (callTool(d, "analyze_profile", { profile_id: 999 }) as any).error,
    "profile_not_found",
  );
});

test("invalid input is rejected by the schema", () => {
  const d = db();
  assert.throws(() => callTool(d, "add_profile", { age: 12 }));
  assert.throws(() => callTool(d, "add_profile", { age: "24" }));
  assert.throws(() => callTool(d, "set_preference", { category: "", value: "x" }));
  assert.throws(() => callTool(d, "save_draft", { draft: "" }));
  assert.throws(() => callTool(d, "get_profile", {}));
  assert.throws(() => callTool(d, "add_profile", { unexpected: 1 }));
  assert.throws(() => callTool(d, "no_such_tool", {}));
});

test("preferences persist and upsert by category", () => {
  const d = db();
  callTool(d, "set_preference", { category: "deal breakers", value: "smoking" });
  callTool(d, "set_preference", { category: "deal breakers", value: "smoking, no hobbies" });
  callTool(d, "set_preference", { category: "interests", value: "coffee, climbing" });
  const prefs = callTool(d, "get_preferences", {}) as any;
  assert.equal(prefs.count, 2);
  const dealBreakers = prefs.preferences.find((p: any) => p.category === "deal breakers");
  assert.equal(dealBreakers.value, "smoking, no hobbies");
});

test("conversations and drafts persist", () => {
  const d = db();
  const { profile_id } = callTool(d, "add_profile", { name: "Sam" }) as any;
  callTool(d, "add_conversation", { profile_id, content: "them: hey\nme: hi" });
  callTool(d, "add_conversation", { profile_id, content: "them: coffee?" });
  const convo = callTool(d, "get_conversation", { profile_id }) as any;
  assert.equal(convo.count, 2);
  assert.match(convo.conversations[0].content, /hey/);

  const saved = callTool(d, "save_draft", { profile_id, draft: "Which roast?" }) as any;
  assert.equal(saved.status, "draft");
  const drafts = callTool(d, "list_drafts", { profile_id }) as any;
  assert.equal(drafts.count, 1);
  assert.equal(drafts.drafts[0].draft, "Which roast?");

  const orphan = callTool(d, "save_draft", { draft: "generic opener" }) as any;
  assert.ok(orphan.draft_id);
  assert.equal((callTool(d, "list_drafts", {}) as any).count, 2);
});

test("draft_reply returns context only and never sends", () => {
  const d = db();
  const { profile_id } = callTool(d, "add_profile", { name: "Sam", bio: "Loves coffee." }) as any;
  callTool(d, "set_preference", { category: "communication style", value: "playful" });
  callTool(d, "add_conversation", { profile_id, content: "them: hey" });
  const ctx = callTool(d, "draft_reply", { profile_id, objective: "ask about their hobby" }) as any;
  assert.equal(ctx.delivery, "manual");
  assert.equal(ctx.objective, "ask about their hobby");
  assert.equal(ctx.preferences.length, 1);
  assert.equal(ctx.conversations.length, 1);
  assert.ok(!("sent" in ctx));
});
