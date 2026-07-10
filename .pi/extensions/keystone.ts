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
				const content = buildCommandPayload(skill, args);
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

type CommandPayloadOptions = {
	packageRoot?: string;
	skillsDir?: string;
	sharedDir?: string;
};

export function buildCommandPayload(skill: string, args: string, options: CommandPayloadOptions = {}): string | null {
	const resolvedPackageRoot = resolve(options.packageRoot ?? packageRoot);
	const resolvedSkillsDir = resolve(options.skillsDir ?? resolve(resolvedPackageRoot, "skills"));
	const skillDir = resolve(resolvedSkillsDir, skill);
	const skillPath = resolve(skillDir, "SKILL.md");
	if (!existsSync(skillPath)) return null;

	const resolvedSharedDir = resolve(options.sharedDir ?? resolve(resolvedSkillsDir, "_shared"));
	const skillContent = stripSkillFrontmatter(readFileSync(skillPath, "utf8"));
	const request = args.trim() || `No request supplied. Briefly explain when to use /${skill} and ask for the task.`;
	return `<EXTREMELY_IMPORTANT>
keystone:${skill} for pi

Use the Keystone \`${skill}\` skill for this request. The canonical packaged skill content is embedded below; follow that embedded content exactly.

Canonical Keystone package root: \`${resolvedPackageRoot}\`.
Embedded skill source: \`${skillPath}\`.
When the embedded skill references a relative path, resolve it against \`${skillDir}\`. Shared gates, handoff packet, and engineering standards live under: \`${resolvedSharedDir}\`.

Pi's built-in coding tools are lowercase: \`read\`, \`write\`, \`edit\`, \`bash\`, plus optional \`grep\`, \`find\`, and \`ls\`.

If \`@tintinweb/pi-subagents\` is installed and the active tool schema exposes them, Pi subagent tool names are \`Agent\`, \`get_subagent_result\`, and \`steer_subagent\`. Follow the embedded skill's subagent guidance for behavior.

<KEYSTONE_SKILL name="${skill}">
${skillContent}
</KEYSTONE_SKILL>

User request:
${request}
</EXTREMELY_IMPORTANT>`;
}

function stripSkillFrontmatter(content: string): string {
	return content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "").trim();
}
