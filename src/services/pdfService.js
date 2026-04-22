const fs = require("fs");
const path = require("path");
const archiver = require("archiver");
const { createBrowser } = require("./browserService");
const { safeFileName } = require("../utils/storage");

async function baixarPdfs(rows, dirs) {
  const browser = await createBrowser();
  const page = await browser.newPage();

  try {
    for (const row of rows) {
      const nomeBase = safeFileName(row.Documento);
      const url = String(row.PDF || "").trim();
      const classificacao = String(row.Classificacao || "").toLowerCase();

      const dirDestino = classificacao === "alta chance"
        ? dirs.altaDir
        : classificacao === "talvez"
          ? dirs.talvezDir
          : null;

      if (!dirDestino || !url) {
        continue;
      }

      let destino = path.join(dirDestino, `${nomeBase}.pdf`);
      let idx = 1;
      while (fs.existsSync(destino)) {
        destino = path.join(dirDestino, `${nomeBase}_${idx}.pdf`);
        idx += 1;
      }

      try {
        await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
        await page.pdf({
          path: destino,
          printBackground: true,
          preferCSSPageSize: true,
        });
      } catch (error) {
        // Ignora falhas individuais para manter o processamento resiliente.
      }
    }
  } finally {
    await page.close();
    await browser.close();
  }
}

function criarZipBuffer(dirPath) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    const archive = archiver("zip", { zlib: { level: 9 } });

    archive.on("data", (data) => chunks.push(data));
    archive.on("warning", (err) => {
      if (err.code === "ENOENT") return;
      reject(err);
    });
    archive.on("error", reject);
    archive.on("end", () => resolve(Buffer.concat(chunks)));

    archive.directory(dirPath, false);
    archive.finalize();
  });
}

module.exports = {
  baixarPdfs,
  criarZipBuffer,
};
