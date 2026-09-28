import test from "node:test";
import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { openDb } from "./db/database.js";
import { createServer } from "./server.js";

test("client -> MCP -> add_profile -> sqlite -> get_profile -> client", async () => {
  const db = openDb(":memory:");
  const server = createServer(db);
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: "test", version: "1.0.0" });
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)]);

  const tools = await client.listTools();
  const names = tools.tools.map((t) => t.name).sort();
  assert.deepEqual(names, [
    "add_conversation",
    "add_profile",
    "analyze_profile",
    "draft_reply",
    "get_conversation",
    "get_preferences",
    "get_profile",
    "list_drafts",
    "list_profiles",
    "save_draft",
    "set_preference",
  ]);

  const created = await client.callTool({
    name: "add_profile",
    arguments: { name: "Sam", age: 24, bio: "Likes hiking and coffee." },
  });
  const { profile_id } = JSON.parse((created as any).content[0].text);
  assert.ok(profile_id > 0);

  const fetched = await client.callTool({
    name: "get_profile",
    arguments: { profile_id },
  });
  const payload = JSON.parse((fetched as any).content[0].text);
  assert.equal(payload.profile.name, "Sam");
  assert.equal(payload.profile.age, 24);

  const missing = await client.callTool({
    name: "get_profile",
    arguments: { profile_id: 4242 },
  });
  assert.equal((missing as any).isError, true);

  await client.close();
  await server.close();
});
