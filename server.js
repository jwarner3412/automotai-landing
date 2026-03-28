const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3001;
const WAITLIST_FILE = path.join(__dirname, "waitlist.json");

// Initialize waitlist file
if (!fs.existsSync(WAITLIST_FILE)) {
  fs.writeFileSync(WAITLIST_FILE, "[]");
}

function readWaitlist() {
  try {
    return JSON.parse(fs.readFileSync(WAITLIST_FILE, "utf8"));
  } catch {
    return [];
  }
}

function writeWaitlist(data) {
  fs.writeFileSync(WAITLIST_FILE, JSON.stringify(data, null, 2));
}

const server = http.createServer((req, res) => {
  // Waitlist API
  if (req.url === "/api/waitlist" && req.method === "POST") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        const { email } = JSON.parse(body);
        if (!email || !email.includes("@")) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Valid email is required" }));
          return;
        }

        const list = readWaitlist();
        const normalized = email.toLowerCase().trim();

        if (list.some((e) => e.email === normalized)) {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ message: "You're already on the list!" }));
          return;
        }

        list.push({ email: normalized, joinedAt: new Date().toISOString() });
        writeWaitlist(list);

        res.writeHead(201, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ message: "You're on the list! We'll be in touch." }));
      } catch {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Something went wrong" }));
      }
    });
    return;
  }

  // Static file serving
  let filePath = req.url === "/" ? "/index.html" : req.url;
  filePath = path.join(__dirname, filePath);

  const ext = path.extname(filePath);
  const mimeTypes = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
  };

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "Content-Type": mimeTypes[ext] || "text/plain" });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`automotAI landing page running at http://localhost:${PORT}`);
});
