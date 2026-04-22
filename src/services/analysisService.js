const axios = require("axios");
const cheerio = require("cheerio");
const { calcularScore } = require("./scoreService");
const { coletarLinksPaginados } = require("./searchService");

async function pegarTextoFast(url) {
  try {
    const response = await axios.get(url, {
      timeout: 12000,
      headers: {
        "User-Agent": "Mozilla/5.0",
      },
    });

    const $ = cheerio.load(response.data);
    const paragrafos = [];
    $(".dou-paragraph").each((_, el) => {
      paragrafos.push($(el).text());
    });

    return paragrafos.join(" ");
  } catch (error) {
    return "";
  }
}

async function processarLink(item) {
  const texto = await pegarTextoFast(item.href);
  const score = calcularScore(texto);

  return {
    Documento: item.titulo,
    PDF: item.href,
    "Score Base": score.scoreBase,
    "Score Representacao": score.scoreRepresentacao,
    "Palavras positivas": score.positivas.join(", "),
    "Palavras negativas": score.negativas.join(", "),
    Bloqueado: score.bloqueado,
  };
}

async function analisarLinks(urlBusca) {
  const links = await coletarLinksPaginados(urlBusca);

  const resultado = [];
  const concorrencia = 10;

  for (let i = 0; i < links.length; i += concorrencia) {
    const lote = links.slice(i, i + concorrencia);
    const processados = await Promise.all(lote.map((item) => processarLink(item)));
    resultado.push(...processados);
  }

  return resultado;
}

module.exports = {
  analisarLinks,
};
