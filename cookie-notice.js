/* Informational notice only. No consent, cookies or browser storage are used. */
(() => {
  'use strict';

  const script = document.currentScript;
  const main = document.querySelector('main');
  const opener = document.querySelector('[data-cookie-notice-open]');
  if (!script || !main || !opener) return;

  const root = new URL('.', script.src);
  const german = document.documentElement.lang.toLowerCase().startsWith('de');
  const copy = german ? {
    title: 'Cookies und Datenschutz',
    description: 'Diese Website verwendet keine eigenen Cookies, Analysedienste oder Werbetracker. Informationen zu den Verbindungsdaten beim Hosting finden Sie in der Datenschutzerklärung.',
    explanation: 'Akzeptieren und Ablehnen schließen nur diesen Hinweis. Es wird keine Einwilligung eingeholt und Ihre Auswahl wird nicht gespeichert. Der Hinweis erscheint bei einem neuen Seitenaufruf erneut.',
    accept: 'Akzeptieren',
    decline: 'Ablehnen',
    links: 'Datenschutzinformationen'
  } : {
    title: 'Cookies and privacy',
    description: 'This website uses no cookies of its own, analytics services or advertising trackers. Our privacy policy explains how connection data is processed by our hosting provider.',
    explanation: 'Accept and Decline only close this notice. No consent is requested and your choice is not stored. The notice appears again when you load a page.',
    accept: 'Accept',
    decline: 'Decline',
    links: 'Privacy information'
  };

  const notice = document.createElement('aside');
  notice.className = 'cookie-notice';
  notice.id = 'cookie-notice-panel';
  notice.setAttribute('aria-labelledby', 'cookie-notice-title');
  notice.innerHTML = `
    <div class="cookie-notice-inner">
      <div class="cookie-notice-copy">
        <h2 id="cookie-notice-title" tabindex="-1">${copy.title}</h2>
        <p>${copy.description}</p>
        <p class="cookie-notice-explanation">${copy.explanation}</p>
        <nav class="cookie-notice-links" aria-label="${copy.links}">
          <a href="${new URL('datenschutz.html#cookie-notice', root)}" lang="de" hreflang="de">Datenschutzerklärung (DE)</a>
          <a href="${new URL('privacy-policy.html#cookie-notice', root)}" lang="en" hreflang="en">Privacy Policy (EN)</a>
        </nav>
      </div>
      <div class="cookie-notice-actions">
        <button type="button" data-cookie-choice="accept">${copy.accept}</button>
        <button type="button" data-cookie-choice="decline">${copy.decline}</button>
      </div>
    </div>`;

  // Normal document flow keeps the page and its legal links accessible.
  main.before(notice);
  const title = notice.querySelector('h2');
  let returnFocus = main;
  opener.setAttribute('aria-controls', notice.id);
  opener.setAttribute('aria-expanded', 'true');

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

  notice.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', closeNotice);
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
    notice.hidden = false;
    opener.setAttribute('aria-expanded', 'true');
    title.focus({ preventScroll: true });
    notice.scrollIntoView({ block: 'start', behavior: 'instant' });
  });
})();
