// 零依赖静态服务器，用于本地预览（npm run dev）
// 支持 --port / --host 参数与 PORT / HOST 环境变量，默认 7100
const http = require("http");
const fs = require("fs");
const path = require("path");

function arg(name, fallback) {
  const i = process.argv.indexOf("--" + name);
  if (i !== -1 && process.argv[i + 1]) return process.argv[i + 1];
  const eq = process.argv.find(a => a.startsWith("--" + name + "="));
  if (eq) return eq.split("=")[1];
  return fallback;
}
const PORT = Number(process.env.PORT || arg("port", 7100));
const HOST = process.env.HOST || arg("host", "127.0.0.1");
const ROOT = __dirname;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
  ".svg": "image/svg+xml", ".webp": "image/webp", ".ico": "image/x-icon",
  ".woff": "font/woff", ".woff2": "font/woff2"
};

http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split("?")[0]);
  let file = path.normalize(path.join(ROOT, urlPath));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end("Forbidden"); }
  if (urlPath.endsWith("/")) file = path.join(file, "index.html");
  fs.stat(file, (err, st) => {
    if (!err && st.isDirectory()) file = path.join(file, "index.html");
    fs.readFile(file, (e, data) => {
      if (e) { res.writeHead(404); return res.end("Not Found"); }
      res.writeHead(200, { "Content-Type": MIME[path.extname(file).toLowerCase()] || "application/octet-stream" });
      res.end(data);
    });
  });
}).listen(PORT, HOST, () => {
  console.log(`✅ 预览服务器已启动: http://${HOST === "0.0.0.0" ? "localhost" : HOST}:${PORT}/`);
});
