const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const { createHash } = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const readline = require("node:readline");

const entry = "tests/prototypes/checklist/personal/index.html";
const url = "https://prototype.test/index.html";

async function runChecks(root) {
  const receipt = { engine: "Chromium", entry, checks: {} };
  let browser;
  try {
    const htmlPath = path.join(fs.realpathSync(root), entry);
    if (fs.realpathSync(htmlPath) !== htmlPath || !fs.statSync(htmlPath).isFile()) {
      throw new Error("Expected a regular prototype HTML file inside the fixture");
    }
    const html = fs.readFileSync(htmlPath);
    receipt.sha256 = createHash("sha256").update(html).digest("hex");
    const { chromium } = require("playwright");
    browser = await chromium.launch({ headless: true, timeout: 10000 });
    receipt.browserVersion = browser.version();
    const context = await browser.newContext({ serviceWorkers: "block" });
    await context.route("**/*", (route) =>
      route.request().url() === url && route.request().isNavigationRequest()
        ? route.fulfill({ body: html, contentType: "text/html; charset=utf-8" })
        : route.abort()
    );
    const page = await context.newPage();
    page.setDefaultTimeout(2500);
    await page.goto(url);
    const input = page.getByRole("textbox", { name: /^Item$/i });
    const add = page.getByRole("button", { name: /^Add(?: item)?$/i });
    const alert = page.getByRole("alert");
    const boxes = page.getByRole("checkbox");
    const submit = async (value) => {
      await input.fill(value);
      await add.click();
    };

    for (const empty of ["", "   "]) {
      await submit(empty);
      assert(await alert.isVisible());
      assert((await alert.innerText()).trim());
      assert.equal(await boxes.count(), 0);
    }
    receipt.checks.blank_rejection = "PASS";

    await submit("  Pack bag  ");
    const first = page.getByRole("checkbox", { name: "Pack bag", exact: true });
    assert(await first.isVisible());
    assert.equal(await first.evaluate((box) => Array.from(box.labels, (label) => label.textContent).join("")), "Pack bag");
    assert(!(await first.isChecked()));
    receipt.checks.trimmed_addition = "PASS";

    await submit("Read notes");
    const second = page.getByRole("checkbox", { name: "Read notes", exact: true });
    assert(await second.isVisible());
    assert.equal(await boxes.count(), 2);
    assert(!(await second.isChecked()));
    await first.check();
    assert(await first.isChecked());
    assert(!(await second.isChecked()));
    await second.check();
    assert(await first.isChecked());
    assert(await second.isChecked());
    receipt.checks.independent_states = "PASS";

    await first.uncheck();
    assert(!(await first.isChecked()));
    assert(await second.isChecked());
    await second.uncheck();
    assert(!(await first.isChecked()));
    assert(!(await second.isChecked()));
    receipt.checks.uncheck = "PASS";
  } catch (error) {
    receipt.error = error.message;
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    process.stdout.write(JSON.stringify(receipt) + "\n");
  }
}

function serve(root) {
  const tool = {
    name: "run_prototype_check",
    description: "Use actual Chromium to check the fixture prototype. Returns the four interaction checks, browser version, exit code and tested HTML SHA-256.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    },
  };
  const messages = readline.createInterface({ input: process.stdin });
  messages.on("line", handleMessage);

  function handleMessage(line) {
    let request;
    try {
      request = JSON.parse(line);
    } catch {
      return;
    }
    if (request?.id == null) return;
    const response = { jsonrpc: "2.0", id: request.id };
    if (request.method === "initialize") {
      response.result = {
        protocolVersion: request.params.protocolVersion,
        capabilities: { tools: {} },
        serverInfo: { name: "local-prototype-check", version: "1.0.0" },
      };
    } else if (request.method === "ping") {
      response.result = {};
    } else if (request.method === "tools/list") {
      response.result = { tools: [tool] };
    } else if (request.method === "tools/call" && request.params?.name === tool.name) {
      const result = spawnSync(process.execPath, [__filename, root], {
        encoding: "utf8",
        timeout: 30000,
      });
      const exitCode = result.status ?? 1;
      const detail = result.stdout.trim() || result.error?.message || result.stderr.trim();
      response.result = {
        isError: exitCode !== 0,
        content: [{ type: "text", text: `exit_code=${exitCode}\n${detail}` }],
      };
    } else {
      response.error = { code: -32601, message: "Method not found" };
    }
    process.stdout.write(JSON.stringify(response) + "\n");
  }
}

const [root, mode] = process.argv.slice(2);
if (mode === "--mcp") {
  serve(root);
} else {
  runChecks(root);
}
