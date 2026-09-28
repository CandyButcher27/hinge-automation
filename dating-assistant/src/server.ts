import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { DatabaseSync } from "node:sqlite";
import { profileTools } from "./tools/profile.js";
import { preferenceTools } from "./tools/preferences.js";
import { messageTools } from "./tools/messages.js";
import { analysisTools } from "./tools/analysis.js";
import type { ToolDef } from "./tools/registry.js";

export const ALL_TOOLS: ToolDef[] = [
  ...profileTools,
  ...preferenceTools,
  ...messageTools,
  ...analysisTools,
];

export function callTool(db: DatabaseSync, name: string, args: unknown) {
  const tool = ALL_TOOLS.find((t) => t.name === name);
  if (!tool) throw new Error(`unknown tool: ${name}`);
  const parsed = z.object(tool.inputSchema).strict().parse(args ?? {});
  return tool.handler(db, parsed);
}

export function createServer(db: DatabaseSync): McpServer {
  const server = new McpServer(
    { name: "dating-assistant", version: "1.0.0" },
    {
      instructions:
        "Local personal dating assistant. It stores only what the user types or pastes in, and it never connects to, scrapes, logs into or automates any dating service. Drafts are for the user to copy and send manually.",
    },
  );

  for (const tool of ALL_TOOLS) {
    server.registerTool(
      tool.name,
      { description: tool.description, inputSchema: tool.inputSchema },
      async (args: any) => {
        const result = tool.handler(db, args ?? {});
        return {
          content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }],
          isError: Boolean((result as any)?.error),
        };
      },
    );
  }

  return server;
}
