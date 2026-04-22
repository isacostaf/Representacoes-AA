const fs = require("fs");
const { Parser } = require("json2csv");

function classificar(row) {
  const scoreBase = Number(row["Score Base"] || 0);
  const scoreRep = Number(row["Score Representacao"] || 0);

  if (scoreRep >= 8) {
    return "Alta chance";
  }
  if (scoreBase > 2) {
    return "Talvez";
  }
  return "Baixa chance";
}

function gerarRelatorio(resumo) {
  const linhas = (resumo || []).map((row) => ({
    Documento: row.Documento,
    PDF: row.PDF,
    Classificacao: classificar(row),
    "Score Base": row["Score Base"],
    "Score Representacao": row["Score Representacao"],
  }));

  const filtradoCsv = linhas.filter((row) => {
    const scoreTotal = Number(row["Score Base"] || 0) + Number(row["Score Representacao"] || 0);
    return scoreTotal > 2;
  });

  return {
    linhas,
    csvRows: filtradoCsv.map((row) => ({
      Documento: row.Documento,
      PDF: row.PDF,
      Classificacao: row.Classificacao,
    })),
  };
}

function salvarCsv(caminho, csvRows) {
  const campos = ["Documento", "PDF", "Classificacao"];
  const parser = new Parser({ fields: campos });

  const conteudo = csvRows && csvRows.length > 0
    ? parser.parse(csvRows)
    : `${campos.join(",")}\n`;

  fs.writeFileSync(caminho, conteudo, "utf8");
  return conteudo;
}

module.exports = {
  gerarRelatorio,
  salvarCsv,
};
