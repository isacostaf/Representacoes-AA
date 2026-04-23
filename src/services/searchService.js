const { createBrowser } = require("./browserService");

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function submeterBusca(page) {
  // Tentativa 1: comportamento mais próximo do Selenium (Enter no campo de busca).
  await page.focus("#search-bar");
  await page.keyboard.press("Enter");

  try {
    await page.waitForNavigation({ waitUntil: "networkidle2", timeout: 15000 });
  } catch (error) {
    // Se não navegar, seguimos para fallback de submit do form.
  }

  if (page.url().includes("/materia")) {
    // Tentativa 2: submit explícito do formulário pai do campo.
    await page.evaluate(() => {
      const input = document.querySelector("#search-bar");
      const form = input ? input.closest("form") : null;
      if (form) {
        form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        if (typeof form.submit === "function") {
          form.submit();
        }
      }
    });

    try {
      await page.waitForNavigation({ waitUntil: "networkidle2", timeout: 15000 });
    } catch (error) {
      // Mantemos fluxo; validação final da URL ocorre abaixo.
    }
  }

  await sleep(1200);
}

async function obterLinkBusca(dataInicialStr, dataFinalStr) {
  const browser = await createBrowser();
  const page = await browser.newPage();

  try {
    await page.goto("https://www.in.gov.br/materia", {
      waitUntil: "networkidle2",
      timeout: 60000,
    });

    await page.waitForSelector("#search-bar", { timeout: 30000 });
    await page.click("#search-bar", { clickCount: 3 });
    await page.type("#search-bar", "Ministerio da Defesa");

    await page.click("#toggle-search-advanced");
    await page.click("label[for='tipo-pesquisa-1']");
    await page.click("label[for='personalizado']");

    await page.evaluate(
      (dataInicial, dataFinal) => {
        const inicio = document.querySelector("#data-inicio");
        const fim = document.querySelector("#data-fim");

        const preencher = (campo, valor) => {
          if (!campo) return;
          campo.removeAttribute("readonly");
          campo.focus();
          campo.value = valor;
          campo.dispatchEvent(new Event("input", { bubbles: true }));
          campo.dispatchEvent(new Event("change", { bubbles: true }));
        };

        preencher(inicio, dataInicial);
        preencher(fim, dataFinal);
      },
      dataInicialStr,
      dataFinalStr
    );

    await submeterBusca(page);

    return page.url();
  } finally {
    await page.close();
    await browser.close();
  }
}

async function coletarLinksPaginados(urlBusca, maxPaginas = 200) {
  const browser = await createBrowser();
  const page = await browser.newPage();

  try {
    await page.goto(urlBusca, {
      waitUntil: "networkidle2",
      timeout: 60000,
    });

    const linksUnicos = [];
    const vistos = new Set();

    for (let pagina = 1; pagina <= maxPaginas; pagina += 1) {
      const resultados = await page.$$eval("a[href*='/web/dou/']", (anchors) =>
        anchors.map((a) => ({
          titulo: (a.textContent || "").trim() || "Sem titulo",
          href: a.href,
        }))
      );

      for (const item of resultados) {
        if (!item.href || vistos.has(item.href)) {
          continue;
        }
        vistos.add(item.href);
        linksUnicos.push(item);
      }

      const hasNext = await page.$("#rightArrow");
      if (!hasNext) {
        break;
      }

      const disabled = await page.$eval("#rightArrow", (btn) => {
        const classes = (btn.getAttribute("class") || "").toLowerCase();
        const ariaDisabled = (btn.getAttribute("aria-disabled") || "").toLowerCase();
        const disabledAttr = btn.getAttribute("disabled");
        return classes.includes("disabled") || ariaDisabled === "true" || disabledAttr !== null;
      });

      if (disabled) {
        break;
      }

      await Promise.all([
        page.click("#rightArrow"),
        sleep(1200),
      ]);
    }

    return linksUnicos;
  } finally {
    await page.close();
    await browser.close();
  }
}

module.exports = {
  obterLinkBusca,
  coletarLinksPaginados,
};
