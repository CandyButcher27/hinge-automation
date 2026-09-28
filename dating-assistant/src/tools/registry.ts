import type { DatabaseSync } from "node:sqlite";
import type { ZodRawShape } from "zod";

export interface ToolDef {
  name: string;
  description: string;
  inputSchema: ZodRawShape;
  handler: (db: DatabaseSync, args: any) => unknown;
}

export function defineTool(def: ToolDef): ToolDef {
  return def;
}
