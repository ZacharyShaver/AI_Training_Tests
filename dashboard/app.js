(function () {
  const data = window.PROJECT_PROGRESS;
  const numberFormatter = new Intl.NumberFormat("en-US");

  const qs = (selector) => document.querySelector(selector);

  function percent(value, target) {
    if (!target) {
      return 0;
    }
    return Math.min(100, (value / target) * 100);
  }

  function basename(path) {
    return path.split(/[\\/]/).pop();
  }

  function repoHref(path) {
    return `../${path.replace(/\\/g, "/")}`;
  }

  function link(path, label) {
    const anchor = document.createElement("a");
    anchor.href = repoHref(path);
    anchor.textContent = label || path;
    anchor.className = "path-link";
    return anchor;
  }

  function renderSummaryCard({ key, title, value, target, note }) {
    const progress = percent(value, target);
    const card = document.createElement("article");
    card.className = `summary-card ${key}`;
    card.innerHTML = `
      <header>
        <h2>${title}</h2>
        <span class="metric-percent">${progress.toFixed(1)}%</span>
      </header>
      <div>
        <p class="metric-value">${numberFormatter.format(value)} <span>/ ${numberFormatter.format(target)}</span></p>
        <p class="metric-note">${note}</p>
      </div>
      <div class="progress-track" aria-hidden="true">
        <div class="progress-fill" style="width: ${progress}%"></div>
      </div>
    `;
    return card;
  }

  function renderSummaries() {
    const combinedTarget = data.goals.buddhist_lines + data.goals.occult_lines;
    const cards = [
      {
        key: "buddhist",
        title: "Buddhist",
        value: data.totals.buddhist_lines,
        target: data.goals.buddhist_lines,
        note: "Final dialogue rows",
      },
      {
        key: "occult",
        title: "Occult / Esoteric",
        value: data.totals.occult_lines,
        target: data.goals.occult_lines,
        note: "Final dialogue rows",
      },
      {
        key: "combined",
        title: "Combined",
        value: data.totals.combined_lines,
        target: combinedTarget,
        note: "Family target sum",
      },
    ];

    const container = qs("#summary-cards");
    container.replaceChildren(...cards.map(renderSummaryCard));
  }

  function renderSourceTables() {
    const groups = Object.values(data.source_groups);
    const tables = groups.map((group) => {
      const sources = data.sources.filter((source) => source.family === group.family);
      const section = document.createElement("section");
      section.className = "family-table";

      const rows = sources
        .map(
          (source) => `
            <tr>
              <td><strong>${source.source}</strong></td>
              <td class="rows-cell">${numberFormatter.format(source.rows)}</td>
              <td data-parser="${source.parser}"></td>
              <td data-output="${source.final_dataset}"></td>
              <td data-vault="${source.vault_note}"></td>
              <td><span class="status-pill">${source.status}</span></td>
            </tr>
          `,
        )
        .join("");

      section.innerHTML = `
        <h3>${group.label}: ${numberFormatter.format(group.lines)} rows</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Rows</th>
                <th>Parser</th>
                <th>Output</th>
                <th>Vault Note</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;

      section.querySelectorAll("[data-parser]").forEach((cell) => {
        cell.replaceChildren(link(cell.dataset.parser, basename(cell.dataset.parser)));
      });
      section.querySelectorAll("[data-output]").forEach((cell) => {
        cell.replaceChildren(link(cell.dataset.output, basename(cell.dataset.output)));
      });
      section.querySelectorAll("[data-vault]").forEach((cell) => {
        cell.replaceChildren(link(cell.dataset.vault, basename(cell.dataset.vault)));
      });
      return section;
    });

    qs("#source-tables").replaceChildren(...tables);
    qs("#source-count").textContent = `${data.sources.length} tracked sources`;
  }

  function renderNextSources() {
    const cards = data.next_sources.map((source) => {
      const card = document.createElement("article");
      card.className = "notice-item";
      card.innerHTML = `
        <h3>${source.source}</h3>
        <p>${source.reason}</p>
      `;
      const artifact = document.createElement("code");
      artifact.appendChild(link(source.current_artifact, source.current_artifact));
      card.appendChild(artifact);
      return card;
    });
    qs("#next-sources").replaceChildren(...cards);
  }

  function renderCleanupNotices() {
    const container = qs("#cleanup-notices");
    const staleDocs = document.createElement("article");
    staleDocs.className = "notice-item";
    staleDocs.innerHTML = `
      <h3>Stale count docs</h3>
      <ul class="doc-list">
        ${data.stale_docs.map((path) => `<li>${path}</li>`).join("")}
      </ul>
    `;

    const notices = data.cleanup_notices.map((notice) => {
      const card = document.createElement("article");
      card.className = "notice-item";
      card.innerHTML = `
        <h3>${notice.path}</h3>
        <p>${notice.reason}</p>
        <code>${notice.status}</code>
      `;
      return card;
    });

    container.replaceChildren(staleDocs, ...notices);
  }

  function render() {
    if (!data) {
      document.body.innerHTML = "<main><p>Dashboard data missing.</p></main>";
      return;
    }

    qs("#generated-at").textContent = data.generated_at;
    renderSummaries();
    renderSourceTables();
    renderNextSources();
    renderCleanupNotices();
  }

  render();
})();
