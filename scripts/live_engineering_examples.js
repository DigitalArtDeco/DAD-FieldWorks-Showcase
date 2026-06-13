(() => {
  const mount = document.getElementById('live-engineering-examples');
  if (!mount) return;
  const dataUrl = mount.dataset.source || 'data/dad_signal_integrity_v0_3_examples.json';
  const fmt = (value, digits = 3) => Number(value).toLocaleString('en-US', { maximumFractionDigits: digits, minimumFractionDigits: digits });
  const flagText = 'ExternallyValidatedQ = False | ProductionAllowedQ = False';

  function badges(items) {
    return `<div class="badge-row">${items.map((item) => `<span>${item}</span>`).join('')}</div>`;
  }

  function metric(label, value, unit = '') {
    return `<div class="metric"><span>${label}</span><strong>${value}${unit ? ` ${unit}` : ''}</strong></div>`;
  }

  function shortTrustStatus(status = '') {
    if (!status) return 'source backed internal record';
    if (status.includes('COMPARISON')) return 'source backed comparison record';
    if (status.includes('INVERSION')) return 'source backed inversion record';
    return 'source backed internal record';
  }

  function claimItems(example) {
    if (Array.isArray(example.claimBoundaryItems)) return example.claimBoundaryItems;
    return String(example.claimBoundary || '')
      .split(';')
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function claimBoundaryList(example) {
    const items = claimItems(example);
    if (!items.length) return '';
    return `<ul class="claim-boundary-list">${items.map((item) => `<li>${item}</li>`).join('')}</ul>`;
  }

  function recordDetail(label, value) {
    if (!value) return '';
    return `<details class="record-detail"><summary>${label}</summary><code>${value}</code></details>`;
  }

  function relationshipChips(items) {
    return `<div class="relationship-chip-row">${items.map((item) => `<span>${item}</span>`).join('')}</div>`;
  }

  function evidenceCard(example) {
    return `<div class="evidence-card"><h4>Evidence / Trust</h4><dl>
      <div><dt>Source Authority</dt><dd>${example.sourceAuthority}</dd></div>
      <div><dt>Trust Status</dt><dd><span class="status-badge" title="${example.trustStatus}" data-full-status="${example.trustStatus}">${shortTrustStatus(example.trustStatus)}</span>${recordDetail('Record detail', example.trustStatus)}</dd></div>
      <div><dt>Claim Boundary</dt><dd>${claimBoundaryList(example)}</dd></div>
      <div><dt>Flags</dt><dd class="flag-row"><span>ExternallyValidatedQ = False</span><span>ProductionAllowedQ = False</span></dd></div>
    </dl></div>`;
  }

  function unavailable(title) {
    return `<article class="live-card locked-card"><h3>${title}</h3><p>This example slot is ready for exported DAD FieldWorks v0.3 example data. No engineering result is shown here until evidence data are available.</p><p><strong>SampleDataQ:</strong> true<br><strong>EngineeringResultQ:</strong> false<br><strong>ForLayoutOnlyQ:</strong> true</p></article>`;
  }

  function renderMicrostrip(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Microstrip 50 Ohm Width Synthesis');
    const widthPercent = Math.max(24, Math.min(88, 24 + item.output.widthToHeightRatio * 20));
    return `<article class="live-card feature-card" id="microstrip-width-synthesis">
      <div class="card-kicker">Width synthesis</div><h3>${item.title}</h3>
      <div class="microstrip-visual" aria-label="Conceptual microstrip cross section"><div class="trace" style="width:${widthPercent}%"></div><div class="substrate"><span>er ${fmt(item.input.relativePermittivity, 1)}</span></div><div class="ground"></div></div>
      <div class="metric-grid">${metric('Target', fmt(item.input.targetImpedanceOhm, 1), 'ohm')}${metric('er', fmt(item.input.relativePermittivity, 1))}${metric('h', fmt(item.input.substrateHeightMm, 1), 'mm')}${metric('Computed width', fmt(item.output.computedWidthMm, 4), 'mm')}${metric('Verification', fmt(item.output.verificationImpedanceOhm, 3), 'ohm')}${metric('Target error', fmt(item.output.targetErrorOhm, 4), 'ohm')}</div>
      ${evidenceCard(item)}
    </article>`;
  }

  function renderCapabilityMap(items) {
    return `<section class="explanation-section live-map" aria-labelledby="capability-map-title"><div class="section-heading"><p class="eyebrow">Signal Integrity v0.3</p><h2 id="capability-map-title">Signal Integrity v0.3 Capability Map</h2><p>All capability cards are bounded internal analytical reference evidence. No card opens an external validation or production claim.</p></div><div class="capability-grid">${items.map((item) => `<article class="capability-card"><h3>${item.family}</h3><p>${item.name}</p>${badges(item.badges)}</article>`).join('')}</div></section>`;
  }

  function renderIpc(item) {
    if (!item || !item.dataAvailableQ) return unavailable('IPC-2141A vs Hammerstad-Jensen Comparison');
    const max = item.summary.maxDeviationPercent;
    return `<article class="live-card" id="ipc-hammerstad-comparison"><div class="card-kicker">Comparison audit</div><h3>${item.title}</h3><div class="deviation-panel"><div class="deviation-bar"><span style="width:${Math.min(max, 100)}%"></span></div><strong>${fmt(max, 2)}%</strong><p>Maximum relative deviation across ${item.summary.caseCount} audited internal comparison cases.</p></div><div class="metric-grid compact">${metric('Case count', item.summary.caseCount, 'cases')}${metric('Mean deviation', fmt(item.summary.meanDeviationPercent, 2), '%')}${metric('Max abs. diff.', fmt(item.summary.maxAbsoluteDifferenceOhm, 2), 'ohm')}</div>${evidenceCard(item)}</article>`;
  }

  function renderStripline(charItem, synthItem) {
    if (!charItem || !synthItem || !charItem.dataAvailableQ || !synthItem.dataAvailableQ) return unavailable('Stripline Analytical Reference Example');
    return `<article class="live-card" id="stripline-example"><div class="card-kicker">Stripline analytical reference</div><h3>${charItem.title}</h3><div class="stripline-visual" aria-label="Conceptual stripline cross section"><div class="plane"></div><div class="strip-center"></div><div class="plane"></div></div><div class="metric-grid">${metric('er', fmt(charItem.input.relativePermittivity, 1))}${metric('Plane spacing', fmt(charItem.input.groundPlaneSeparationMm, 2), 'mm')}${metric('Conductor width', fmt(charItem.input.conductorWidthMm, 2), 'mm')}${metric('Z0', fmt(charItem.output.characteristicImpedanceOhm, 3), 'ohm')}${metric('Synth width', fmt(synthItem.output.computedWidthMm, 3), 'mm')}${metric('Synth error', fmt(synthItem.output.targetErrorOhm, 4), 'ohm')}</div>${evidenceCard(charItem)}</article>`;
  }

  function renderCoupled(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Coupled Line Even/Odd Mode');
    return `<article class="live-card" id="coupled-line-even-odd"><div class="card-kicker">Even / odd modal record</div><h3>${item.title}</h3><div class="coupled-visual" aria-label="Conceptual coupled line mode drawing"><div class="coupled-trace even">+</div><div class="coupled-trace odd">-</div></div><p class="concept-note">${item.conceptualDrawingNote}</p><div class="metric-grid compact">${metric('Z0e', fmt(item.output.z0eOhm, 3), 'ohm')}${metric('Z0o', fmt(item.output.z0oOhm, 3), 'ohm')}${metric('C', fmt(item.output.C, 3))}${metric('K', fmt(item.output.K, 3))}</div>${evidenceCard(item)}</article>`;
  }

  function renderDifferential(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Differential Pair Spacing Sweep');
    const rows = item.rows;
    const buttons = rows.map((row, index) => `<button type="button" class="spacing-button${index === 1 ? ' active' : ''}" data-index="${index}">${fmt(row.spacingMm, 2)} mm</button>`).join('');
    const start = rows[1] || rows[0];
    return `<article class="live-card" id="differential-pair-sweep"><div class="card-kicker">Spacing sweep</div><h3>${item.title}</h3><div class="diff-visual" aria-label="Conceptual differential pair drawing"><div class="diff-trace"></div><div class="diff-gap" id="diff-gap-visual"></div><div class="diff-trace"></div></div><p class="concept-note">${item.conceptualDrawingNote}</p><div class="spacing-controls">${buttons}</div><div class="metric-grid compact" id="diff-metrics">${metric('Spacing', fmt(start.spacingMm, 2), 'mm')}${metric('Zdiff', fmt(start.zdiffOhm, 3), 'ohm')}${metric('Zcommon', fmt(start.zcommonOhm, 3), 'ohm')}${metric('K', fmt(start.K, 3))}</div>${relationshipChips(item.relationshipNotes)}${evidenceCard(item)}</article>`;
  }

  function renderBeyond(items) {
    return `<section class="explanation-section" aria-labelledby="beyond-v03-title"><div class="section-heading"><p class="eyebrow">Beyond v0.3</p><h2 id="beyond-v03-title">Future routes stay closed until evidence exists.</h2><p>These directions are not presented as implemented public results.</p></div><div class="future-grid">${items.map((item) => `<article class="future-card"><h3>${item.name}</h3><span>${item.status}</span><p>${item.publicClaim}</p></article>`).join('')}</div></section>`;
  }

  function attachDiffControls(data) {
    const card = document.getElementById('differential-pair-sweep');
    if (!card) return;
    const metrics = card.querySelector('#diff-metrics');
    const gap = card.querySelector('#diff-gap-visual');
    card.querySelectorAll('.spacing-button').forEach((button) => {
      button.addEventListener('click', () => {
        card.querySelectorAll('.spacing-button').forEach((b) => b.classList.remove('active'));
        button.classList.add('active');
        const row = data.rows[Number(button.dataset.index)];
        metrics.innerHTML = `${metric('Spacing', fmt(row.spacingMm, 2), 'mm')}${metric('Zdiff', fmt(row.zdiffOhm, 3), 'ohm')}${metric('Zcommon', fmt(row.zcommonOhm, 3), 'ohm')}${metric('K', fmt(row.K, 3))}`;
        gap.style.width = `${Math.max(20, Math.min(80, row.normalizedGapG * 46))}px`;
      });
    });
  }

  fetch(dataUrl).then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then((data) => {
    mount.innerHTML = `${renderMicrostrip(data.microstripWidthSynthesis)}${renderCapabilityMap(data.capabilityMap)}<div class="live-grid">${renderIpc(data.ipcHammerstadComparison)}${renderStripline(data.striplineCharacteristicImpedance, data.striplineWidthSynthesis)}${renderCoupled(data.coupledLineEvenOdd)}${renderDifferential(data.differentialPairSpacingSweep)}</div>${renderBeyond(data.beyondV03)}`;
    attachDiffControls(data.differentialPairSpacingSweep);
  }).catch(() => {
    mount.innerHTML = '<article class="live-card locked-card"><h3>Live examples unavailable</h3><p>The public data file could not be loaded. No engineering result is shown without evidence data.</p></article>';
  });
})();
