(() => {
  const mount = document.getElementById('live-engineering-examples');
  if (!mount) return;

  const dataUrl = mount.dataset.source || 'data/dad_signal_integrity_v0_3_examples.json';
  const fmt = (value, digits = 3) => Number(value).toLocaleString('en-US', {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits
  });

  const evidenceChips = [
    'internal alpha',
    'source backed',
    'analytical reference',
    'not externally validated',
    'not production ready',
    'not full wave EM simulation'
  ];

  function chips(items) {
    return `<div class="chip-row">${items.map((item) => `<span>${item}</span>`).join('')}</div>`;
  }

  function metric(label, value, unit = '') {
    return `<div class="metric"><span>${label}</span><strong>${value}${unit ? ` ${unit}` : ''}</strong></div>`;
  }

  function statusBar() {
    return `<div class="example-status">${chips(evidenceChips)}</div>`;
  }

  function unavailable(title) {
    return `<article class="example-card muted-card"><h3>${title}</h3><p>No public engineering result is shown until evidence data are available.</p>${chips(['awaiting exported data', 'no public result'])}</article>`;
  }

  function renderMicrostrip(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Microstrip design example');
    const widthPercent = Math.max(24, Math.min(88, 24 + item.output.widthToHeightRatio * 20));
    return `<article class="example-feature" id="microstrip-width-synthesis">
      <div>
        <p class="card-kicker">Featured example</p>
        <h3>Microstrip 50 Ohm Width Synthesis</h3>
        <p class="example-lead">A target impedance is inverted to a trace width and immediately checked against the analytical reference model.</p>
        ${statusBar()}
      </div>
      <div class="example-workbench">
        <div class="microstrip-visual" aria-label="Conceptual microstrip cross section"><div class="trace" style="width:${widthPercent}%"></div><div class="substrate"><span>er ${fmt(item.input.relativePermittivity, 1)}</span></div><div class="ground"></div></div>
        <div class="metric-grid">${metric('Target', fmt(item.input.targetImpedanceOhm, 1), 'ohm')}${metric('er', fmt(item.input.relativePermittivity, 1))}${metric('h', fmt(item.input.substrateHeightMm, 1), 'mm')}${metric('Width', fmt(item.output.computedWidthMm, 4), 'mm')}${metric('Verification', fmt(item.output.verificationImpedanceOhm, 3), 'ohm')}${metric('Error', fmt(item.output.targetErrorOhm, 4), 'ohm')}</div>
      </div>
    </article>`;
  }

  function renderCapabilityMap(items) {
    return `<section class="capability-summary" aria-labelledby="capability-map-title">
      <div>
        <p class="card-kicker">Capability map</p>
        <h3 id="capability-map-title">Signal Integrity v0.3 baseline</h3>
      </div>
      <div class="capability-pills">${items.map((item) => `<span>${item.family}</span>`).join('')}</div>
    </section>`;
  }

  function renderComparison(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Analytical reference family comparison');
    return `<article class="example-card" id="reference-family-comparison">
      <p class="card-kicker">Reference family comparison</p>
      <h3>${item.title}</h3>
      <div class="comparison-figure"><strong>${fmt(item.summary.maxDeviationPercent, 2)}%</strong><span>maximum relative deviation</span></div>
      <div class="metric-grid compact">${metric('Cases', item.summary.caseCount)}${metric('Mean', fmt(item.summary.meanDeviationPercent, 2), '%')}${metric('Max diff.', fmt(item.summary.maxAbsoluteDifferenceOhm, 2), 'ohm')}</div>
      ${chips(['two analytical reference families', 'one evidence boundary'])}
    </article>`;
  }

  function renderStripline(charItem, synthItem) {
    if (!charItem || !synthItem || !charItem.dataAvailableQ || !synthItem.dataAvailableQ) return unavailable('Stripline analytical reference');
    return `<article class="example-card" id="stripline-example">
      <p class="card-kicker">Transmission line reference</p>
      <h3>Stripline Analytical Reference</h3>
      <div class="stripline-visual" aria-label="Conceptual stripline cross section"><div class="plane"></div><div class="strip-center"></div><div class="plane"></div></div>
      <div class="metric-grid compact">${metric('er', fmt(charItem.input.relativePermittivity, 1))}${metric('Spacing', fmt(charItem.input.groundPlaneSeparationMm, 2), 'mm')}${metric('Z0', fmt(charItem.output.characteristicImpedanceOhm, 3), 'ohm')}${metric('Width check', fmt(synthItem.output.computedWidthMm, 3), 'mm')}</div>
      ${chips(['source backed', 'analytical reference'])}
    </article>`;
  }

  function renderCoupled(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Coupled line even/odd model');
    return `<article class="example-card" id="coupled-line-even-odd">
      <p class="card-kicker">Coupled line</p>
      <h3>Even/Odd Analytical Model</h3>
      <div class="coupled-visual" aria-label="Conceptual coupled line mode drawing"><div class="coupled-trace even">+</div><div class="coupled-trace odd">-</div></div>
      <p class="concept-note">Conceptual illustration only.</p>
      <div class="metric-grid compact">${metric('Z0e', fmt(item.output.z0eOhm, 3), 'ohm')}${metric('Z0o', fmt(item.output.z0oOhm, 3), 'ohm')}${metric('C', fmt(item.output.C, 3))}${metric('K', fmt(item.output.K, 3))}</div>
      ${chips(['internal alpha', 'not full wave EM simulation'])}
    </article>`;
  }

  function renderDifferential(item) {
    if (!item || !item.dataAvailableQ) return unavailable('Differential pair derived quantities');
    const start = item.rows[1] || item.rows[0];
    return `<article class="example-card" id="differential-pair-sweep">
      <p class="card-kicker">Differential pair</p>
      <h3>Spacing Sweep</h3>
      <div class="diff-visual" aria-label="Conceptual differential pair drawing"><div class="diff-trace"></div><div class="diff-gap"></div><div class="diff-trace"></div></div>
      <div class="metric-grid compact">${metric('Spacing', fmt(start.spacingMm, 2), 'mm')}${metric('Zdiff', fmt(start.zdiffOhm, 3), 'ohm')}${metric('Zcommon', fmt(start.zcommonOhm, 3), 'ohm')}${metric('K', fmt(start.K, 3))}</div>
      ${chips(['derived from modal outputs', 'conceptual drawing'])}
    </article>`;
  }

  function renderBeyond(items) {
    return `<section class="future-summary" aria-labelledby="future-routes-title">
      <div>
        <p class="card-kicker">Future routes</p>
        <h3 id="future-routes-title">Closed until evidence exists.</h3>
      </div>
      <div class="capability-pills">${items.map((item) => `<span>${item.name}</span>`).join('')}</div>
    </section>`;
  }

  fetch(dataUrl).then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then((data) => {
    mount.innerHTML = `<div class="examples-suite">
      ${renderMicrostrip(data.microstripWidthSynthesis)}
      ${renderCapabilityMap(data.capabilityMap)}
      <div class="example-grid">
        ${renderComparison(data.formulaFamilyComparison)}
        ${renderStripline(data.striplineCharacteristicImpedance, data.striplineWidthSynthesis)}
        ${renderCoupled(data.coupledLineEvenOdd)}
        ${renderDifferential(data.differentialPairSpacingSweep)}
      </div>
      ${renderBeyond(data.beyondV03)}
    </div>`;
  }).catch(() => {
    mount.innerHTML = '<article class="example-card muted-card"><h3>Engineering examples unavailable</h3><p>The public data file could not be loaded. No engineering result is shown without evidence data.</p></article>';
  });
})();
