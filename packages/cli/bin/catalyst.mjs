#!/usr/bin/env node
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";

const REPO_URL = "https://github.com/prathamarchives/catalyst.git";

function usage() {
  console.log(`Catalyst local launcher

Usage:
  catalyst local [--repo <path>] [--no-open]
  catalyst --help
  catalyst --version

Examples:
  npx catalyst local
  npx @trycatalyst/cli local
  node packages/cli/bin/catalyst.mjs local --repo C:/Users/Rakesh/Desktop/catalyst --no-open

The launcher never asks for secrets. It starts the local Python engine at
http://127.0.0.1:8765. Stop it with Ctrl+C.`);
}

function parse(argv) {
  const args = { command: null, repo: "", noOpen: false, help: false, version: false };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--help" || a === "-h") args.help = true;
    else if (a === "--version" || a === "-v") args.version = true;
    else if (a === "--no-open") args.noOpen = true;
    else if (a === "--repo") {
      args.repo = argv[i + 1] || "";
      i += 1;
    } else if (!args.command) {
      args.command = a;
    } else {
      throw new Error(`unknown argument: ${a}`);
    }
  }
  return args;
}

function localInstallDir() {
  const home = os.homedir();
  return path.join(home, ".catalyst", "local");
}

function isRepo(dir) {
  return !!dir && existsSync(path.join(dir, "catalyst.py")) && existsSync(path.join(dir, "apps", "control-panel", "server.py"));
}

function findPython() {
  const candidates = process.platform === "win32"
    ? [{ cmd: "py", args: ["-3"] }, { cmd: "python", args: [] }, { cmd: "python3", args: [] }]
    : [{ cmd: "python3", args: [] }, { cmd: "python", args: [] }];
  for (const c of candidates) {
    const probe = spawnSync(c.cmd, [...c.args, "--version"], { stdio: "ignore" });
    if (probe.status === 0) return c;
  }
  return null;
}

function ensureRepoInstall(dir) {
  if (isRepo(dir)) return dir;
  mkdirSync(path.dirname(dir), { recursive: true });
  const git = spawnSync("git", ["--version"], { stdio: "ignore" });
  if (git.status !== 0) {
    throw new Error(`Catalyst is not installed at ${dir} and git was not found. Clone ${REPO_URL} there, or rerun with --repo <checkout>.`);
  }
  console.log(`Installing Catalyst into ${dir}`);
  const cloned = spawnSync("git", ["clone", "--depth", "1", REPO_URL, dir], { stdio: "inherit" });
  if (cloned.status !== 0) throw new Error("git clone failed");
  return dir;
}

function resolveRepo(repoArg) {
  if (repoArg) {
    const resolved = path.resolve(repoArg);
    if (!isRepo(resolved)) throw new Error(`--repo does not look like a Catalyst checkout: ${resolved}`);
    return resolved;
  }
  if (isRepo(process.cwd())) return process.cwd();
  return ensureRepoInstall(localInstallDir());
}

function runLocal(args) {
  const python = findPython();
  if (!python) throw new Error("Python was not found. Install Python 3, then rerun Catalyst.");
  const repo = resolveRepo(args.repo);
  const script = path.join(repo, "catalyst.py");
  const pyArgs = [...python.args, script];
  if (args.noOpen) pyArgs.push("--no-open");

  console.log(`Catalyst repo: ${repo}`);
  console.log("URL: http://127.0.0.1:8765");
  console.log("Stop server: press Ctrl+C in this terminal.");

  const child = spawn(python.cmd, pyArgs, {
    cwd: repo,
    stdio: "inherit",
    env: { ...process.env, CATALYST_LAUNCHED_BY: "npm-cli" },
  });
  child.on("exit", (code, signal) => {
    if (signal) process.exit(0);
    process.exit(code ?? 0);
  });
}

try {
  const args = parse(process.argv.slice(2));
  if (args.help || !args.command) {
    usage();
  } else if (args.version) {
    console.log("0.1.0");
  } else if (args.command === "local") {
    runLocal(args);
  } else {
    throw new Error(`unknown command: ${args.command}`);
  }
} catch (err) {
  console.error(`Catalyst error: ${err.message}`);
  process.exit(1);
}
