// Browser version of passguard/strength.py and passguard/breach.py.

const COMMON_PASSWORDS = new Set([
  "123456", "password", "123456789", "12345678", "12345", "qwerty", "abc123",
  "football", "1234567", "monkey", "111111", "letmein", "1234", "1234567890",
  "dragon", "baseball", "sunshine", "iloveyou", "trustno1", "princess",
  "admin", "welcome", "master", "login", "passw0rd", "starwars", "shadow",
  "superman", "qwerty123", "hello", "freedom", "whatever", "123123", "654321",
  "michael", "football1", "charlie", "aa123456", "donald", "qwertyuiop",
]);
const KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"];
const LEET = { "@": "a", "4": "a", "3": "e", "1": "i", "!": "i", "0": "o", "$": "s", "5": "s", "7": "t" };
const PUNCTUATION = /[!-\/:-@\[-`{-~ ]/;
const GUESSES_PER_SECOND = 1e10;
const LABELS = ["Very weak", "Weak", "Fair", "Strong", "Very strong"];
const COLORS = ["var(--red)", "var(--orange)", "var(--yellow)", "var(--green)", "var(--green)"];

function charsetSize(pw) {
  let size = 0;
  if (/[a-z]/.test(pw)) size += 26;
  if (/[A-Z]/.test(pw)) size += 26;
  if (/[0-9]/.test(pw)) size += 10;
  if (PUNCTUATION.test(pw)) size += 33;
  if (/[^\x00-\x7F]/.test(pw)) size += 100;
  return size;
}

function isCommon(pw) {
  const lowered = pw.toLowerCase();
  const leet = [...lowered].map((c) => LEET[c] ?? c).join("");
  const stripped = lowered.replace(/[0-9!-\/:-@\[-`{-~]+$/, "");
  return COMMON_PASSWORDS.has(lowered) || COMMON_PASSWORDS.has(leet)
    || (stripped.length >= 4 && COMMON_PASSWORDS.has(stripped));
}

function hasKeyboardPattern(pw, minLen = 4) {
  const lowered = pw.toLowerCase();
  for (const row of KEYBOARD_ROWS) {
    for (const seq of [row, [...row].reverse().join("")]) {
      for (let i = 0; i <= seq.length - minLen; i++) {
        if (lowered.includes(seq.slice(i, i + minLen))) return true;
      }
    }
  }
  return false;
}

function effectiveLength(pw) {
  if (!pw) return 0;
  let length = 1;
  for (let i = 1; i < pw.length; i++) {
    length += Math.abs(pw.charCodeAt(i) - pw.charCodeAt(i - 1)) <= 1 ? 0.25 : 1;
  }
  return length;
}

function formatDuration(seconds) {
  if (seconds < 1) return "instantly";
  const units = [["century", 3.15576e9], ["year", 3.15576e7], ["month", 2.6298e6],
    ["day", 86400], ["hour", 3600], ["minute", 60], ["second", 1]];
  for (const [name, size] of units) {
    if (seconds >= size) {
      const value = seconds / size;
      if (name === "century" && value >= 1e6) return "millions of centuries";
      const n = Math.floor(value);
      const plural = name === "century" ? "centuries" : name + "s";
      return `${n} ${n === 1 ? name : plural}`;
    }
  }
  return "instantly";
}

function analyze(pw) {
  const warnings = [];
  const suggestions = [];
  const pool = charsetSize(pw);
  let entropy = pool ? effectiveLength(pw) * Math.log2(pool) : 0;

  if (isCommon(pw)) {
    warnings.push("This is one of the most common passwords.");
    entropy = Math.min(entropy, 10);
  }
  if (hasKeyboardPattern(pw)) {
    warnings.push("Contains a keyboard pattern (e.g. 'qwerty', '1234').");
    entropy *= 0.7;
  }
  if (effectiveLength(pw) < pw.length * 0.75) {
    warnings.push("Contains repeated or sequential characters (e.g. 'aaa', 'abc').");
  }

  if (pw.length < 12) suggestions.push("Use at least 12 characters - length matters most.");
  if (!/[A-Z]/.test(pw) || !/[a-z]/.test(pw)) suggestions.push("Mix uppercase and lowercase letters.");
  if (!/[0-9]/.test(pw)) suggestions.push("Add some numbers.");
  if (!PUNCTUATION.test(pw)) suggestions.push("Add symbols like ! ? # %.");
  if (warnings.length) suggestions.push("Try a passphrase of 4+ random words, e.g. 'violet-tractor-lamp-river'.");

  const score = entropy < 28 ? 0 : entropy < 36 ? 1 : entropy < 60 ? 2 : entropy < 80 ? 3 : 4;
  const seconds = 2 ** entropy / 2 / GUESSES_PER_SECOND;
  return { length: pw.length, entropy: Math.round(entropy * 10) / 10, score,
    label: LABELS[score], crackTime: formatDuration(seconds), warnings, suggestions };
}

// k-anonymity: only the first 5 hex chars of the SHA-1 hash are sent to the API.
async function pwnedCount(pw) {
  const digest = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(pw));
  const hash = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("").toUpperCase();
  const prefix = hash.slice(0, 5);
  const suffix = hash.slice(5);
  const res = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`, { headers: { "Add-Padding": "true" } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  for (const line of (await res.text()).split("\n")) {
    const [candidate, count] = line.trim().split(":");
    if (candidate === suffix) return parseInt(count, 10);
  }
  return 0;
}

// ---- UI ----
const $ = (id) => document.getElementById(id);
const input = $("password");
const breachBtn = $("breach-btn");
const breachOut = $("breach");

function fillList(el, items) {
  el.replaceChildren(...items.map((text) => Object.assign(document.createElement("li"), { textContent: text })));
}

input.addEventListener("input", () => {
  const pw = input.value;
  breachOut.textContent = "";
  breachBtn.disabled = !pw;
  if (!pw) {
    $("meter-fill").style.width = "0";
    $("label").innerHTML = "&nbsp;";
    ["length", "entropy", "crack"].forEach((id) => ($(id).textContent = "-"));
    fillList($("warnings"), []);
    fillList($("suggestions"), []);
    return;
  }
  const r = analyze(pw);
  $("meter-fill").style.width = `${(r.score + 1) * 20}%`;
  $("meter-fill").style.background = COLORS[r.score];
  $("label").textContent = r.label;
  $("label").style.color = COLORS[r.score];
  $("length").textContent = r.length;
  $("entropy").textContent = `${r.entropy} bits`;
  $("crack").textContent = r.crackTime;
  fillList($("warnings"), r.warnings.map((w) => `⚠ ${w}`));
  fillList($("suggestions"), r.suggestions);
});

breachBtn.addEventListener("click", async () => {
  breachBtn.disabled = true;
  breachOut.style.color = "var(--muted)";
  breachOut.textContent = "Checking...";
  try {
    const count = await pwnedCount(input.value);
    breachOut.style.color = count ? "var(--red)" : "var(--green)";
    breachOut.textContent = count
      ? `🚨 Found ${count.toLocaleString()} times in data breaches. Don't use it!`
      : "✅ Not found in any known data breach.";
  } catch (err) {
    breachOut.style.color = "var(--yellow)";
    breachOut.textContent = `Could not reach Have I Been Pwned (${err.message}).`;
  } finally {
    breachBtn.disabled = !input.value;
  }
});

$("toggle").addEventListener("click", () => {
  const hidden = input.type === "password";
  input.type = hidden ? "text" : "password";
  $("toggle").textContent = hidden ? "Hide" : "Show";
});
