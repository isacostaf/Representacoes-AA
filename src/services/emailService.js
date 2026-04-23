const fs = require("fs");
const path = require("path");
const nodemailer = require("nodemailer");

function listarDestinatarios() {
  const raw = process.env.EMAIL_TO || "";
  return raw
    .replace(/;/g, ",")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function montarCorpoEmail(alta, talvez) {
  if (!alta.length && !talvez.length) {
    return [
      "Prezados,",
      "",
      "Informamos que, na consulta realizada hoje, nao foram identificadas representacoes.",
      "",
      "Atenciosamente,",
      "Equipe de Monitoramento",
    ].join("\n");
  }

  const listaAlta = alta.length ? alta.map((n) => `- ${n}`).join("\n") : "- Nenhum arquivo nesta categoria";
  const listaTalvez = talvez.length ? talvez.map((n) => `- ${n}`).join("\n") : "- Nenhum arquivo nesta categoria";

  return [
    "Prezados,",
    "",
    "Informamos que foram identificadas representacoes na consulta realizada hoje.",
    "Seguem abaixo os documentos localizados:",
    "",
    "Arquivos de Alta chance:",
    listaAlta,
    "",
    "Arquivos de Talvez:",
    listaTalvez,
    "",
    "Encaminhamos em anexo o relatorio CSV e os arquivos PDF correspondentes.",
    "",
    "Atenciosamente,",
    "Equipe de Monitoramento",
  ].join("\n");
}

function listarPdfsParaAnexo(pdfBase) {
  if (!fs.existsSync(pdfBase)) {
    return [];
  }

  const stack = [pdfBase];
  const files = [];

  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(fullPath);
        continue;
      }

      if (entry.isFile() && entry.name.toLowerCase().endsWith(".pdf")) {
        files.push(fullPath);
      }
    }
  }

  return files.sort((a, b) => a.localeCompare(b));
}

async function enviarEmail({ csvPath, pdfBase, linhas }) {
  const smtpHost = process.env.SMTP_HOST;
  const smtpPort = Number(process.env.SMTP_PORT || 0);
  const smtpUser = process.env.SMTP_USER;
  const smtpPassword = process.env.SMTP_PASSWORD;
  const emailFrom = process.env.EMAIL_FROM || smtpUser;
  const destinatarios = listarDestinatarios();

  if (!smtpHost || !smtpPort || !smtpUser || !smtpPassword || !destinatarios.length) {
    throw new Error("Configuracao SMTP incompleta no .env.");
  }

  const alta = linhas.filter((l) => l.Classificacao === "Alta chance").map((l) => l.Documento);
  const talvez = linhas.filter((l) => l.Classificacao === "Talvez").map((l) => l.Documento);

  const transporter = nodemailer.createTransport({
    host: smtpHost,
    port: smtpPort,
    secure: smtpPort === 465,
    auth: {
      user: smtpUser,
      pass: smtpPassword,
    },
  });

  const anexos = [];
  if (fs.existsSync(csvPath)) {
    anexos.push({ filename: path.basename(csvPath), path: csvPath });
  }

  for (const pdfPath of listarPdfsParaAnexo(pdfBase)) {
    anexos.push({ filename: path.basename(pdfPath), path: pdfPath });
  }

  await transporter.sendMail({
    from: emailFrom,
    to: destinatarios.join(", "),
    subject: `Representacoes ${new Date().toLocaleDateString("pt-BR")}`,
    text: montarCorpoEmail(alta, talvez),
    attachments: anexos,
  });
}

module.exports = {
  enviarEmail,
};
