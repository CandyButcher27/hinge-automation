#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { openDb } from "./db/database.js";
import { createServer } from "./server.js";

const db = openDb();
const server = createServer(db);
await server.connect(new StdioServerTransport());
