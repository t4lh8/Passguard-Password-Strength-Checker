// Animated background: the most common leaked passwords drifting upward and slowly spinning.

// Collected from yearly "most common passwords" lists (NordPass, SplashData, HIBP, RockYou).
const WORDS = [
  // numbers
  "123456", "123456789", "12345678", "12345", "1234567", "1234567890", "1234",
  "111111", "123123", "654321", "000000", "666666", "121212", "112233", "123321",
  "7777777", "888888", "987654321", "159753", "147258369", "123654", "55555",
  "11111111", "999999", "131313", "0987654321", "1111", "123", "12341234",
  // keyboard walks
  "qwerty", "qwerty123", "qwertyuiop", "1q2w3e4r", "1qaz2wsx", "zaq12wsx", "asdfgh",
  "asdfghjkl", "zxcvbnm", "qazwsx", "1q2w3e", "q1w2e3r4", "qwe123", "asd123",
  "1q2w3e4r5t", "qwer1234", "zxcvbn", "azerty", "qwertz", "!@#$%^&*",
  // words
  "password", "password1", "password123", "passw0rd", "p@ssw0rd", "Password1!",
  "admin", "admin123", "administrator", "root", "toor", "guest", "user", "test",
  "test123", "letmein", "welcome", "welcome1", "login", "master", "access",
  "secret", "changeme", "default", "iloveyou", "trustno1", "whatever", "hello",
  "freedom", "sunshine", "princess", "dragon", "monkey", "shadow", "superman",
  "batman", "starwars", "pokemon", "football", "baseball", "soccer", "hockey",
  "basketball", "michael", "charlie", "jordan", "jennifer", "hunter", "hunter2",
  "ashley", "jessica", "daniel", "thomas", "robert", "donald", "maggie", "ginger",
  "cookie", "chocolate", "summer", "flower", "lovely", "loveme", "babygirl",
  "angel", "tigger", "buster", "pepper", "killer", "ninja", "mustang", "ferrari",
  "computer", "internet", "matrix", "google", "facebook", "samsung", "iphone",
  "cheese", "banana", "orange", "purple", "silver", "golden", "blink182",
  "abc123", "aa123456", "a123456", "abcd1234", "abc12345", "iloveyou1", "qwerty1",
  "letmein1", "monkey1", "dragon1", "superman1", "football1", "princess1",
  // international
  "senha", "motdepasse", "contraseña", "passwort", "parola", "sifre", "sifre123",
  "galatasaray", "fenerbahce", "besiktas", "Password123", "PASSWORD",
];

const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let width = 0;
let height = 0;
let particles = [];

function spawn(anywhere) {
  const danger = Math.random() < 0.15;  // a few words glow red, like a breach alert
  return {
    text: WORDS[Math.floor(Math.random() * WORDS.length)],
    x: Math.random() * width,
    y: anywhere ? Math.random() * height : height + 40,
    size: 11 + Math.random() * 18,
    speed: 0.15 + Math.random() * 0.5,
    drift: (Math.random() - 0.5) * 0.2,
    angle: (Math.random() - 0.5) * 0.6,
    spin: (Math.random() - 0.5) * 0.004,
    alpha: 0.06 + Math.random() * 0.14,
    color: danger ? "248, 81, 73" : "139, 148, 158",
  };
}

function resize() {
  const dpr = window.devicePixelRatio || 1;
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const count = Math.min(130, Math.floor((width * height) / 11000));
  particles = Array.from({ length: count }, () => spawn(true));
}

function draw() {
  ctx.clearRect(0, 0, width, height);
  for (const p of particles) {
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.angle);
    ctx.font = `${p.size}px ui-monospace, Consolas, monospace`;
    ctx.fillStyle = `rgba(${p.color}, ${p.alpha})`;
    ctx.fillText(p.text, 0, 0);
    ctx.restore();
  }
}

function tick() {
  for (let i = 0; i < particles.length; i++) {
    const p = particles[i];
    p.y -= p.speed;
    p.x += p.drift;
    p.angle += p.spin;
    if (p.y < -40) particles[i] = spawn(false);
  }
  draw();
  requestAnimationFrame(tick);
}

window.addEventListener("resize", () => {
  resize();
  if (reducedMotion) draw();
});
resize();
if (reducedMotion) draw();
else requestAnimationFrame(tick);
