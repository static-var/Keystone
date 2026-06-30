/**
 * keystone-models — /keystone-models cascade picker for per-route model
 * & reasoning-effort overrides. Writes to ~/.config/keystone/models.json.
 *
 * v1 scope (intentionally minimal):
 *   2 scopes: defaults | routes
 *   routes are derived dynamically from skills/keystone/modules/*.md via ROUTES
 *   per-entry: model (string) + optional thinking level (6 values)
 *   picker: ctx.ui.select for each cascade level (no custom TUI)
 *
 * v2 candidates: sequences.<workflow>.<step> scope, project-local file,
 * warn-on-miss validator, custom TUI with type-to-filter, runtime applier.
 */
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { getSupportedThinkingLevels, type Model } from "@earendil-works/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import { ROUTES } from "../keystone.js";

const CONFIG_PATH = join(homedir(), ".config", "keystone", "models.json");

const THINKING_LEVELS = ["off", "minimal", "low", "medium", "high", "xhigh"] as const;
type ThinkingLevel = (typeof THINKING_LEVELS)[number];

type Entry = string | { model?: string; thinking?: ThinkingLevel };
type Config = { defaults?: Entry; routes?: Record<string, Entry> };

function load(): Config {
	try {
		const raw: unknown = JSON.parse(readFileSync(CONFIG_PATH, "utf8"));
		return validate(raw) ? raw : {};
	} catch {
		return {};
	}
}

function save(config: Config): boolean {
	try {
		mkdirSync(dirname(CONFIG_PATH), { recursive: true });
		writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
		return true;
	} catch {
		return false;
	}
}

function validate(raw: unknown): raw is Config {
	if (!raw || typeof raw !== "object" || Array.isArray(raw)) return false;
	const r = raw as Record<string, unknown>;
	if (
		r.defaults !== undefined &&
		typeof r.defaults !== "string" &&
		(typeof r.defaults !== "object" || r.defaults === null || Array.isArray(r.defaults))
	) {
		return false;
	}
	for (const k of ["routes", "subagents"] as const) {
		const v = r[k];
		if (v !== undefined && (typeof v !== "object" || v === null || Array.isArray(v))) return false;
	}
	return true;
}

function modelKey(m: Pick<Model<never>, "provider" | "id">): string {
	return `${m.provider}/${m.id}`;
}

function describeEntry(e: Entry): string {
	if (typeof e === "string") return e;
	const t = e.thinking ? ` (${e.thinking})` : "";
	return `${e.model ?? ""}${t}`;
}

async function pickScope(ctx: ExtensionContext): Promise<string | undefined> {
	const c = load();
	const mark = (n: number) => ` (${n} set)`;
	const items: string[] = [
		`defaults${c.defaults !== undefined ? mark(1) : ""}`,
		`routes${c.routes && Object.keys(c.routes).length ? mark(Object.keys(c.routes).length) : ""}`,
		"reset all overrides",
	];
	return ctx.ui.select("Select scope", items);
}

async function pickKey(ctx: ExtensionContext, scope: string): Promise<string | undefined> {
	if (scope === "defaults") return "";
	const c = load();
	const items = ROUTES.map((r) => {
		const e = c.routes?.[r];
		return e ? `${r}  ${describeEntry(e)}` : r;
	});
	return ctx.ui.select("Select route", items);
}

async function pickModel(ctx: ExtensionContext): Promise<string | undefined> {
	const available = ctx.modelRegistry.getAvailable();
	if (available.length === 0) {
		ctx.ui.notify("No models available (no API keys configured?).", "error");
		return undefined;
	}
	return ctx.ui.select("Select model", available.map((m) => modelKey(m)));
}

type EffortChoice = ThinkingLevel | "inherit" | undefined;

async function pickEffort(ctx: ExtensionContext, m: string): Promise<EffortChoice> {
	const picked = ctx.modelRegistry.getAvailable().find((x) => modelKey(x) === m);
	if (!picked?.reasoning) return "inherit";
	const supported = getSupportedThinkingLevels(picked);
	const items: string[] = ["inherit (no override)"];
	if (supported.includes("off")) items.push("off (disable reasoning)");
	for (const level of THINKING_LEVELS) {
		if (level === "off") continue;
		if (supported.includes(level)) items.push(level);
	}
	const choice = await ctx.ui.select("Reasoning effort", items);
	if (choice === undefined) return undefined;
	if (choice.startsWith("inherit")) return "inherit";
	if (choice.startsWith("off")) return "off";
	return choice as ThinkingLevel;
}

function applyEntry(config: Config, scope: string, key: string, entry: Entry): void {
	if (scope === "defaults") {
		config.defaults = entry;
	} else if (scope === "routes") {
		config.routes = { ...(config.routes ?? {}), [key]: entry };
	}
}

async function runCascade(ctx: ExtensionContext): Promise<void> {
	while (true) {
		const scope = await pickScope(ctx);
		if (scope === undefined) return;
		const isReset = scope.startsWith("reset all");
		if (isReset) {
			const ok = await ctx.ui.confirm(
				"Reset ALL model overrides?",
				"This clears every override in ~/.config/keystone/models.json. Cannot be undone.",
			);
			if (ok) {
				save({});
				ctx.ui.notify("All overrides cleared.", "info");
			} else {
				ctx.ui.notify("Reset cancelled.", "info");
			}
			continue;
		}
		const scopeKey = scope.split(" ")[0] as "defaults" | "routes";
		const rawKey = await pickKey(ctx, scopeKey);
		if (rawKey === undefined) continue;
		const key = rawKey.split(" ")[0];
		const model = await pickModel(ctx);
		if (model === undefined) continue;
		const effort = await pickEffort(ctx, model);
		if (effort === undefined) continue;
		const entry: Entry = effort === "inherit" ? model : { model, thinking: effort };
		const config = load();
		applyEntry(config, scopeKey, key, entry);
		if (save(config)) {
			const effortLabel = effort === "inherit" ? "" : ` (${effort})`;
			ctx.ui.notify(`Saved ${scopeKey}${key ? `/${key}` : ""} → ${model}${effortLabel}`, "info");
		} else {
			ctx.ui.notify("Failed to save models.json (disk error or permissions).", "error");
		}
	}
}

export function registerKeystoneModelsCommand(pi: ExtensionAPI): void {
	pi.registerCommand("keystone-models", {
		description: "Configure per-route model & effort overrides (saved to ~/.config/keystone/models.json)",
		handler: async (_args, ctx) => {
			if (!ctx.hasUI) {
				ctx.ui.notify("/keystone-models requires an interactive UI session.", "error");
				return;
			}
			await runCascade(ctx);
		},
	});
}

// Runtime applier: reads ~/.config/keystone/models.json on agent_start and
// applies the matching override. Cascade: routes.<currentRoute> → defaults.
// The baseline (model + thinking level) is snapshotted before each apply and
// restored at agent_end, because pi.setModel persists to disk. currentRoute
// is set by either the keystone command handler (when the user invokes
// /keystone <route>) or the model itself emitting <!-- keystone:route=NAME -->
// in its response (which the context-event parser in keystone.ts picks up).
// Any other invocation clears it so defaults applies.
let currentRoute: string | undefined;

export function setCurrentRoute(route: string | undefined): void {
	currentRoute = route;
}

export function registerKeystoneModelsApplier(pi: ExtensionAPI): void {
	let baselineModel: Model<any> | undefined;
	let baselineThinking: ThinkingLevel | undefined;

	async function applyEntry(ctx: { modelRegistry: { find: (p: string, id: string) => Model<any> | undefined } }, entry: Entry): Promise<void> {
		const modelStr = typeof entry === "string" ? entry : entry.model;
		const thinking = typeof entry === "string" ? undefined : entry.thinking;

		if (modelStr) {
			const slash = modelStr.indexOf("/");
			if (slash > 0 && slash < modelStr.length - 1) {
				const model = ctx.modelRegistry.find(modelStr.slice(0, slash), modelStr.slice(slash + 1));
				if (model) {
					await pi.setModel(model);
				}
			}
		}

		if (thinking) {
			pi.setThinkingLevel(thinking);
		}
	}

	pi.on("agent_start", async (_event, ctx) => {
		const config = load();

		const entry: Entry | undefined =
			(currentRoute && config.routes?.[currentRoute]) || config.defaults;
		if (!entry) return;

		baselineModel = ctx.model;
		baselineThinking = pi.getThinkingLevel() as ThinkingLevel;

		await applyEntry(ctx, entry);
	});

	pi.on("agent_end", async () => {
		if (!baselineModel) return;
		if (baselineModel) {
			await pi.setModel(baselineModel);
		}
		if (baselineThinking) {
			pi.setThinkingLevel(baselineThinking);
		}
		baselineModel = undefined;
		baselineThinking = undefined;
		currentRoute = undefined;
	});
}

