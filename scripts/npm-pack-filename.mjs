import { readFile } from "node:fs/promises";

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function packageEntries(packOutput) {
  if (Array.isArray(packOutput)) {
    return packOutput;
  }

  if (packOutput && typeof packOutput === "object") {
    return Object.values(packOutput);
  }

  return [];
}

function validateFilename(filename) {
  return (
    typeof filename === "string" &&
    /^[^/\\]+\.tgz$/.test(filename) &&
    !filename.includes("..")
  );
}

async function main() {
  const input = process.argv[2]
    ? await readFile(process.argv[2], "utf8")
    : await readStdin();

  let packOutput;
  try {
    packOutput = JSON.parse(input);
  } catch (error) {
    throw new Error(`Unable to parse npm pack JSON: ${error.message}`);
  }

  const [entry] = packageEntries(packOutput);
  if (!entry) {
    throw new Error("npm pack output did not include a package entry");
  }

  const { filename } = entry;
  if (!validateFilename(filename)) {
    throw new Error("npm pack filename must be a local .tgz filename");
  }

  process.stdout.write(`${filename}\n`);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
