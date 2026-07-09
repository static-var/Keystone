import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const extensionDir = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(extensionDir, "../..");
const skillsDir = resolve(packageRoot, "skills");

const publicSkills = readdirSync(skillsDir, { withFileTypes: true })
	.filter((entry) => entry.isDirectory() && !entry.name.startsWith("_") && existsSync(resolve(skillsDir, entry.name, "SKILL.md")))
	.map((entry) => entry.name)
	.sort();

function skillDescription(skill: string): string {
	const content = readFileSync(resolve(skillsDir, skill, "SKILL.md"), "utf8");
	return content.match(/^description:\s*(.+)$/m)?.[1]?.trim().replace(/^['"]|['"]$/g, "")
		?? `Use the Keystone ${skill} skill`;
}

export default function keystonePiExtension(pi: ExtensionAPI) {
	pi.on("resources_discover", async () => ({
		skillPaths: [skillsDir],
	}));

	for (const skill of publicSkills) {
		pi.registerCommand(skill, {
			description: skillDescription(skill),
			handler: async (args, ctx) => {
				const content = getCommandContent(skill, args);
				if (!content) {
					ctx.ui.notify(`Keystone skill not found: ${skill}`, "error");
					return;
				}

				if (ctx.isIdle()) {
					pi.sendUserMessage(content);
				} else {
					pi.sendUserMessage(content, { deliverAs: "followUp" });
					ctx.ui.notify(`Queued Keystone ${skill} as a follow-up.`, "info");
				}
			},
		});
	}
}

function getCommandContent(skill: string, args: string): string | null {
	const skillPath = resolve(skillsDir, skill, "SKILL.md");
	if (!existsSync(skillPath)) return null;
	const request = args.trim() || `No request supplied. Briefly explain when to use /${skill} and ask for the task.`;
	return `<EXTREMELY_IMPORTANT>
keystone:${skill} for pi

Use the Keystone \`${skill}\` skill for this request. Load and follow \`skills/${skill}/SKILL.md\` exactly. Resolve shared gates, handoff packet, and engineering standards relative to \`skills/\`.

Pi's built-in coding tools are lowercase: \`read\`, \`write\`, \`edit\`, \`bash\`, plus optional \`grep\`, \`find\`, and \`ls\`.

If \`@tintinweb/pi-subagents\` is installed and the active tool schema exposes them, Pi subagent tool names are \`Agent\`, \`get_subagent_result\`, and \`steer_subagent\`. Follow the canonical Keystone subagent guidance for behavior.

User request:
${request}
</EXTREMELY_IMPORTANT>`;
}
