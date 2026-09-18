/* One optional preference cookie, written only after explicit consent.
 * Hosting requests cannot be blocked by client-side cookie controls.
 * Keep the cookie version and published privacy text aligned when changing purpose.
 */
(() => {
  'use strict';

  const script = document.currentScript;
  const main = document.querySelector('main');
  const opener = document.querySelector('[data-cookie-notice-open]');
  if (!script || !main || !opener) return;

  const root = new URL('.', script.src);
  const cookieName = '__Host-dadlabs_notice';
  const cookieVersion = 'v2';
  const maxAge = 180 * 24 * 60 * 60;
  const german = document.documentElement.lang.toLowerCase().startsWith('de');
  const copy = german ? {
    title: 'Cookie-Einstellungen',
    description: 'DigitalArtDeco Labs möchte mit Ihrer Einwilligung einen optionalen Cookie speichern, damit dieser Hinweis 180 Tage geschlossen bleibt. „Cookie akzeptieren“ erlaubt genau diesen Cookie. „Ablehnen“ setzt ihn nicht. Wir verwenden keine Analyse- oder Werbetracker.',
    hosting: 'GitHub Pages hostet diese Website und protokolliert IP-Adressen zu Sicherheitszwecken. Daten können auch außerhalb des EWR, etwa in den USA, verarbeitet werden. Diese Hosting-Verarbeitung findet unabhängig von Ihrer Cookie-Auswahl statt.',
    explanation: 'Sie können Ihre Einwilligung jederzeit über „Cookie-Einstellungen“ am Seitenende widerrufen. Ohne den optionalen Cookie erscheint der Hinweis bei einem neuen Seitenaufruf erneut. Alle Inhalte bleiben zugänglich.',
    accept: 'Cookie akzeptieren',
    decline: 'Ablehnen',
    close: 'Schließen',
    withdraw: 'Einwilligung widerrufen',
    enabled: 'Der optionale Cookie ist aktiviert. Er unterdrückt diesen Hinweis für höchstens 180 Tage ab Ihrer Zustimmung. Mit „Einwilligung widerrufen“ löschen Sie ihn. Wir verwenden keine Analyse- oder Werbetracker.',
    details: 'Cookie-Details und Empfänger',
    detailText: 'Anbieter: DigitalArtDeco Labs UG (haftungsbeschränkt). Zweck: diesen Hinweis bei weiteren Seitenaufrufen geschlossen halten. Name: __Host-dadlabs_notice. Inhalt: v2, ohne individuelle Kennung. Laufzeit: 180 Tage, ohne automatische Verlängerung. Gültig nur auf diesem Host. Der Browser sendet den Cookie bei weiteren Anfragen an GitHub Pages, auch an Infrastruktur außerhalb des EWR. Einzelheiten stehen in der Datenschutzerklärung.',
    saveError: 'Der Browser konnte den Cookie nicht speichern. Ihre Zustimmung wurde nicht gespeichert. Sie können ohne Cookie fortfahren.',
    deleteError: 'Der Cookie konnte nicht gelöscht werden. Bitte entfernen Sie ihn in den Website-Dateneinstellungen Ihres Browsers.',
    links: 'Datenschutzinformationen'
  } : {
    title: 'Cookie settings',
    description: 'With your consent, DigitalArtDeco Labs would like to store one optional cookie to keep this notice closed for 180 days. Accept cookie allows only this cookie. Decline leaves it unset. We do not use analytics or advertising trackers.',
    hosting: 'GitHub Pages hosts this website and logs IP addresses for security. Data may also be processed outside the EEA, including the USA. This hosting processing takes place regardless of your cookie choice.',
    explanation: 'You can withdraw consent at any time through Cookie settings at the bottom of every page. Without the optional cookie, this notice appears again when you load a page. All content remains accessible.',
    accept: 'Accept cookie',
    decline: 'Decline',
    close: 'Close',
    withdraw: 'Withdraw consent',
    enabled: 'The optional cookie is enabled. It keeps this notice closed for up to 180 days from your consent. Withdraw consent deletes it. We do not use analytics or advertising trackers.',
    details: 'Cookie details and recipients',
    detailText: 'Provider: DigitalArtDeco Labs UG (haftungsbeschränkt). Purpose: keep this notice closed on subsequent page loads. Name: __Host-dadlabs_notice. Content: v2, with no individual identifier. Lifetime: 180 days, with no automatic renewal. Valid only on this host. Your browser sends the cookie with subsequent requests to GitHub Pages, including infrastructure outside the EEA. See the privacy policy for details.',
    saveError: 'Your browser could not save the cookie. Your consent has not been stored. You can continue without the cookie.',
    deleteError: 'The cookie could not be deleted. Please remove it using your browser’s website data settings.',
    links: 'Privacy information'
  };

  function readPreference() {
    try {
      const prefix = `${cookieName}=`;
      const item = document.cookie.split(';').map(value => value.trim()).find(value => value.startsWith(prefix));
      return item ? item.slice(prefix.length) : null;
    } catch {
      return null;
    }
  }

  function setPreference(value, lifetime) {
    try {
      document.cookie = `${cookieName}=${value}; Max-Age=${lifetime}; Path=/; Secure; SameSite=Lax`;
    } catch {
      // Verification below keeps the UI honest when browser storage is blocked.
    }
    return lifetime === 0 ? readPreference() === null : readPreference() === value;
  }

  const notice = document.createElement('aside');
  notice.className = 'cookie-notice';
  notice.id = 'cookie-notice-panel';
  notice.setAttribute('aria-labelledby', 'cookie-notice-title');
  notice.innerHTML = `
    <div class="cookie-notice-inner">
      <div class="cookie-notice-copy">
        <h2 id="cookie-notice-title" tabindex="-1">${copy.title}</h2>
        <p class="cookie-notice-purpose">${copy.description}</p>
        <p class="cookie-notice-hosting">${copy.hosting}</p>
        <p class="cookie-notice-explanation">${copy.explanation}</p>
        <details class="cookie-notice-details"><summary>${copy.details}</summary><p>${copy.detailText}</p></details>
        <nav class="cookie-notice-links" aria-label="${copy.links}">
          <a href="${new URL('datenschutz.html#cookie-notice', root)}" lang="de" hreflang="de">Datenschutzerklärung (DE)</a>
          <a href="${new URL('privacy-policy.html#cookie-notice', root)}" lang="en" hreflang="en">Privacy Policy (EN)</a>
        </nav>
        <p class="cookie-notice-error" role="status" hidden></p>
      </div>
      <div class="cookie-notice-actions">
        <button type="button" data-cookie-choice="accept">${copy.accept}</button>
        <button type="button" data-cookie-choice="decline">${copy.decline}</button>
      </div>
    </div>`;

  // Normal document flow keeps the page and its legal links accessible.
  main.before(notice);
  const title = notice.querySelector('h2');
  const accept = notice.querySelector('[data-cookie-choice="accept"]');
  const decline = notice.querySelector('[data-cookie-choice="decline"]');
  const status = notice.querySelector('[role="status"]');
  let returnFocus = main;
  let enabled = readPreference() === cookieVersion;
  notice.hidden = enabled;
  opener.setAttribute('aria-controls', notice.id);
  opener.setAttribute('aria-expanded', String(!notice.hidden));

  function refreshChoices() {
    enabled = readPreference() === cookieVersion;
    notice.querySelector('.cookie-notice-purpose').textContent = enabled ? copy.enabled : copy.description;
    accept.textContent = enabled ? copy.close : copy.accept;
    decline.textContent = enabled ? copy.withdraw : copy.decline;
    status.hidden = true;
    status.textContent = '';
  }
  refreshChoices();

  function showError(message) {
    status.textContent = message;
    status.hidden = false;
  }

  function closeNotice() {
    const focusWasInside = notice.contains(document.activeElement);
    notice.hidden = true;
    opener.setAttribute('aria-expanded', 'false');
    if (focusWasInside) {
      const hadTabindex = returnFocus.hasAttribute('tabindex');
      if (!hadTabindex) returnFocus.setAttribute('tabindex', '-1');
      returnFocus.focus({ preventScroll: true });
      if (!hadTabindex) returnFocus.removeAttribute('tabindex');
    }
  }

  accept.addEventListener('click', () => {
    if (enabled) {
      closeNotice();
    } else if (setPreference(cookieVersion, maxAge)) {
      enabled = true;
      closeNotice();
    } else {
      showError(copy.saveError);
    }
  });
  decline.addEventListener('click', () => {
    // A fresh decline writes nothing. Withdrawal removes only our named cookie.
    if (readPreference() !== null && !setPreference('', 0)) {
      showError(copy.deleteError);
      return;
    }
    enabled = false;
    closeNotice();
  });
  notice.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      event.preventDefault();
      closeNotice();
    }
  });
  opener.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    returnFocus = opener;
    refreshChoices();
    notice.hidden = false;
    opener.setAttribute('aria-expanded', 'true');
    title.focus({ preventScroll: true });
    notice.scrollIntoView({ block: 'start', behavior: 'instant' });
  });
})();
