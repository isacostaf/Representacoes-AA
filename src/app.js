require("dotenv").config();

const fs = require("fs");
const path = require("path");
const express = require("express");
const { v4: uuidv4 } = require("uuid");

const { createRunDirs } = require("./utils/storage");
const { obterLinkBusca } = require("./services/searchService");
const { analisarLinks } = require("./services/analysisService");
const { gerarRelatorio, salvarCsv } = require("./services/reportService");
const { baixarPdfs, criarZipBuffer } = require("./services/pdfService");
const { enviarEmail } = require("./services/emailService");
const { saveRun, getRun } = require("./state");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(process.cwd(), "views"));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get("/", (req, res) => {
  const hoje = new Date().toISOString().slice(0, 10);

  res.render("index", {
    dataInicial: hoje,
    dataFinal: hoje,
    erro: "",
    aviso: "",
    runId: "",
    rows: [],
  });
});

app.post("/process", async (req, res) => {
  const dataInicial = String(req.body.dataInicial || "");
  const dataFinal = String(req.body.dataFinal || "");

  if (!dataInicial || !dataFinal || dataInicial > dataFinal) {
    return res.status(400).render("index", {
      dataInicial,
      dataFinal,
      erro: "A data inicial nao pode ser maior que a data final.",
      aviso: "",
      runId: "",
      rows: [],
    });
  }

  const [anoI, mesI, diaI] = dataInicial.split("-");
  const [anoF, mesF, diaF] = dataFinal.split("-");
  const dataInicialStr = `${diaI}/${mesI}/${anoI}`;
  const dataFinalStr = `${diaF}/${mesF}/${anoF}`;

  try {
    const runId = uuidv4();
    const dirs = createRunDirs(runId);

    const urlBusca = await obterLinkBusca(dataInicialStr, dataFinalStr);
    const resumo = await analisarLinks(urlBusca);

    const relatorio = gerarRelatorio(resumo);
    salvarCsv(dirs.csvPath, relatorio.csvRows);

    await baixarPdfs(relatorio.linhas, dirs);

    saveRun(runId, {
      dataInicial,
      dataFinal,
      rows: relatorio.linhas,
      dirs,
    });

    const totalDocumentos = resumo.length;
    const totalClassificados = relatorio.csvRows.length;
    let aviso = "";

    if (totalDocumentos === 0) {
      aviso = "Nenhum documento foi retornado pela busca para o periodo informado.";
    } else if (totalClassificados === 0) {
      aviso = `Foram encontrados ${totalDocumentos} documento(s), mas nenhum atingiu o criterio minimo de classificacao.`;
    }

    return res.render("index", {
      dataInicial,
      dataFinal,
      erro: "",
      aviso,
      runId,
      rows: relatorio.linhas,
    });
  } catch (error) {
    return res.status(500).render("index", {
      dataInicial,
      dataFinal,
      erro: `Falha no processamento: ${error.message}`,
      aviso: "",
      runId: "",
      rows: [],
    });
  }
});

app.get("/download/csv/:runId", (req, res) => {
  const run = getRun(req.params.runId);
  if (!run || !fs.existsSync(run.dirs.csvPath)) {
    return res.status(404).send("Arquivo nao encontrado.");
  }

  return res.download(run.dirs.csvPath, "relatorio.csv");
});

app.get("/download/zip/:runId/:tipo", async (req, res) => {
  const run = getRun(req.params.runId);
  if (!run) {
    return res.status(404).send("Processamento nao encontrado.");
  }

  const tipo = req.params.tipo;
  const dir = tipo === "alta"
    ? run.dirs.altaDir
    : tipo === "talvez"
      ? run.dirs.talvezDir
      : "";

  if (!dir || !fs.existsSync(dir)) {
    return res.status(404).send("Pasta nao encontrada.");
  }

  try {
    const zip = await criarZipBuffer(dir);
    const fileName = tipo === "alta" ? "alta_chance.zip" : "talvez.zip";
    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", `attachment; filename=${fileName}`);
    return res.send(zip);
  } catch (error) {
    return res.status(500).send(`Falha ao gerar ZIP: ${error.message}`);
  }
});

app.post("/email/:runId", async (req, res) => {
  const run = getRun(req.params.runId);
  if (!run) {
    return res.status(404).send("Processamento nao encontrado.");
  }

  try {
    await enviarEmail({
      csvPath: run.dirs.csvPath,
      pdfBase: run.dirs.pdfBase,
      linhas: run.rows,
    });

    return res.redirect("/");
  } catch (error) {
    return res.status(500).send(`Falha ao enviar e-mail: ${error.message}`);
  }
});

module.exports = app;
