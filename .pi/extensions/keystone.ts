import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const EXTREMELY_IMPORTANT_MARKER = "<EXTREMELY_IMPORTANT>";
const BOOTSTRAP_MARKER = "keystone:bootstrap for pi";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(extensionDir, "../..");
const skillsDir = resolve(packageRoot, "skills");
const keystoneSkillPath = resolve(skillsDir, "keystone", "SKILL.md");

let cachedSkillBody: string | null | undefined;
let cachedBootstrap: string | null | undefined;

export default function keystonePiExtension(pi: ExtensionAPI) {
	let injectBootstrap = true;

	pi.on("resources_discover", async () => ({
		skillPaths: [skillsDir],
	}));

	pi.on("session_start", async () => {
		injectBootstrap = true;
	});

	pi.on("session_compact", async () => {
		injectBootstrap = true;
	});

	pi.on("agent_end", async () => {
		injectBootstrap = false;
	});

	pi.on("context", async (event) => {
		if (!injectBootstrap) return;
		if (event.messages.some(messageContainsBootstrap)) return;

		const bootstrap = getBootstrapContent();
		if (!bootstrap) return;

		const bootstrapMessage = {
			role: "user" as const,
			content: [{ type: "text" as const, text: bootstrap }],
			timestamp: Date.now(),
		};

		const insertAt = firstNonCompactionSummaryIndex(event.messages);
		return {
			messages: [
				...event.messages.slice(0, insertAt),
				bootstrapMessage,
				...event.messages.slice(insertAt),
			],
		};
	});

	pi.registerCommand("keystone", {
		description: "Run the Keystone workflow router on a request",
		handler: async (args, ctx) => {
			const content = getCommandContent(args);
			if (!content) {
				ctx.ui.notify("Keystone skill not found in this package.", "error");
				return;
			}

			if (ctx.isIdle()) {
				pi.sendUserMessage(content);
			} else {
				pi.sendUserMessage(content, { deliverAs: "followUp" });
				ctx.ui.notify("Queued Keystone as a follow-up.", "info");
			}
		},
	});
}

function getBootstrapContent(): string | null {
	if (cachedBootstrap !== undefined) return cachedBootstrap;

	const body = getSkillBody();
	if (!body) {
		cachedBootstrap = null;
		return null;
	}

	cachedBootstrap = `${EXTREMELY_IMPORTANT_MARKER}
${BOOTSTRAP_MARKER}

Keystone is available in this Pi session.

Use Keystone when the user invokes \`/keystone\` or explicitly asks for Keystone/workflow routing. Otherwise continue normally and do not override user intent.

The Keystone entrypoint is included below. When Keystone applies, follow it and route internally by reading the chosen module files. Do not expose internal modules as public slash commands.

${body}

${piToolMapping()}
</EXTREMELY_IMPORTANT>`;
	return cachedBootstrap;
}

function getCommandContent(args: string): string | null {
	const body = getSkillBody();
	if (!body) return null;

	const request = args.trim() || "No request supplied. Briefly explain how to use `/keystone <task>` and ask for the task.";
	return `${EXTREMELY_IMPORTANT_MARKER}
${BOOTSTRAP_MARKER}

You are running Keystone via Pi's \`/keystone\` command.

Follow the Keystone entrypoint below. Route internally by reading the chosen module files. Do not expose internal modules as public slash commands.

${body}

${piToolMapping()}

User request for Keystone:
${request}
</EXTREMELY_IMPORTANT>`;
}

function getSkillBody(): string | null {
	if (cachedSkillBody !== undefined) return cachedSkillBody;

	try {
		cachedSkillBody = stripFrontmatter(readFileSync(keystoneSkillPath, "utf8"));
		return cachedSkillBody;
	} catch {
		cachedSkillBody = null;
		return null;
	}
}

function stripFrontmatter(content: string): string {
	const match = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
	return (match ? match[1] : content).trim();
}

function piToolMapping(): string {
	return `## Pi tool mapping

Pi has native skills, but Keystone should use this extension's \`/keystone\` command as the public entrypoint. Internal Keystone modules are Markdown files under \`skills/keystone/modules/\`; read the selected module file instead of inventing \`/shape\`, \`/breakdown\`, \`/build\`, \`/debug\`, \`/review\`, \`/ship\`, \`/health\`, or other public module commands.

Pi's built-in coding tools are lowercase: \`read\`, \`write\`, \`edit\`, \`bash\`, plus optional \`grep\`, \`find\`, and \`ls\`. Use those for file inspection, mutation, shell commands, and search.

If \`pi-subagents\` or another subagent tool is available, follow Keystone's \`modules/helpers/subagents.md\` guidance. If no subagent tool is available, do the work in this session and state that delegation was unavailable instead of inventing unsupported tools.`;
}

function messageContainsBootstrap(message: unknown): boolean {
	const content = (message as { content?: unknown }).content;
	if (typeof content === "string") return content.includes(BOOTSTRAP_MARKER);
	if (!Array.isArray(content)) return false;
	return content.some((part) => {
		return (
			part &&
			typeof part === "object" &&
			(part as { type?: unknown }).type === "text" &&
			typeof (part as { text?: unknown }).text === "string" &&
			(part as { text: string }).text.includes(BOOTSTRAP_MARKER)
		);
	});
}

function firstNonCompactionSummaryIndex(messages: unknown[]): number {
	let index = 0;
	while ((messages[index] as { role?: unknown } | undefined)?.role === "compactionSummary") {
		index += 1;
	}
	return index;
}
