#!/usr/bin/env node
// Read the lock and fingerprint companion files without invoking npm or the app.
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../../../../", import.meta.url));
const sha256 = (data) => createHash("sha256").update(data).digest("hex");
const read = (name) => readFileSync(join(root, name));
const fingerprint = (name) => {
  try {
    return sha256(read(name));
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
};

function filesUnder(directory) {
  try {
    return readdirSync(join(root, directory), { withFileTypes: true })
      .flatMap((entry) => {
        const name = join(directory, entry.name);
        if (entry.isDirectory()) return filesUnder(name);
        return entry.isFile() ? [name] : [];
      })
      .sort();
  } catch (error) {
    if (error.code === "ENOENT") return [];
    throw error;
  }
}

try {
  const manifest = JSON.parse(read("package.json"));
  if (
    manifest.name !== "nickmoreton" ||
    !statSync(join(root, "webapp")).isDirectory()
  ) {
    throw new Error("This skill is specific to the nickmoreton.co.uk checkout");
  }
  const lockBytes = read("package-lock.json");
  const lock = JSON.parse(lockBytes);
  if (!lock.packages || ![2, 3].includes(lock.lockfileVersion)) {
    throw new Error("Expected npm lockfile v2/v3 with package-path entries");
  }
  const paths = new Set([
    "package.json",
    "package-lock.json",
    ".nvmrc",
    "docker/Dockerfile",
    ".pre-commit-config.yaml",
    "biome.json",
    "Makefile",
    "app.json",
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "docs/node-upgrade.md",
    "docs/local.production.md",
    "docs/data-and-media.md",
    "docker-compose.yaml",
    "docker-compose.production.yaml",
    ...filesUnder(".github/workflows"),
    ...filesUnder("scripts"),
    ...filesUnder("webapp/static_src"),
  ]);
  const packages = Object.entries(lock.packages)
    .filter(([name]) => name !== "")
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([path, entry]) => ({
      path,
      name: entry.name ?? path.split("node_modules/").at(-1),
      version: entry.version ?? null,
      integrity: entry.integrity ?? null,
      // Avoid printing potentially private registry/git URLs or local paths.
      source_sha256: sha256(JSON.stringify(entry.resolved ?? null)),
      metadata_sha256: sha256(JSON.stringify(entry)),
      engines: entry.engines ?? {},
      os: entry.os ?? [],
      cpu: entry.cpu ?? [],
      libc: entry.libc ?? [],
      dev: entry.dev ?? false,
      optional: entry.optional ?? false,
      link: entry.link ?? false,
      has_install_script: entry.hasInstallScript ?? false,
    }));
  const direct = Object.fromEntries(
    [
      "dependencies",
      "devDependencies",
      "optionalDependencies",
      "peerDependencies",
    ].map((kind) => [kind, Object.keys(manifest[kind] ?? {}).sort()]),
  );
  process.stdout.write(
    `${JSON.stringify(
      {
        schema_version: 1,
        project: manifest.name,
        engines: manifest.engines ?? {},
        node_version_file: read(".nvmrc").toString().trim(),
        script_names: Object.keys(manifest.scripts ?? {}).sort(),
        direct_dependencies: direct,
        lock: {
          sha256: sha256(lockBytes),
          version: lock.lockfileVersion,
          packages,
        },
        companion_files: Object.fromEntries(
          [...paths].sort().map((name) => [name, fingerprint(name)]),
        ),
      },
      null,
      2,
    )}\n`,
  );
} catch (error) {
  // Do not echo malformed JSON/source contents in error messages.
  const message =
    error instanceof SyntaxError ? "Invalid project JSON" : error.message;
  process.stderr.write(`Inventory failed: ${message}\n`);
  process.exitCode = 1;
}
