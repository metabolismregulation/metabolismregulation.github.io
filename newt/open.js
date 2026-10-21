// Added to our copy of Newt by tools/newt_build.sh (open.js, after Newt's bundle.js): a Newt button of
// the website's Converter or ysbgn.js page links /newt/?f=<key>#<file name>; Newt opened there asks that
// page for the file over a BroadcastChannel (inside the browser) and loads it through its own file
// input, as if dropped. A link, so a click, a middle click and "Open link in new tab" all work (user,
// 2026-10-21). The cookie skips Newt's welcome tour.
(function () {
  var key = new URLSearchParams(location.search).get('f');
  if (!key) return;
  document.cookie = 'showIntro=false; path=' + location.pathname + '; max-age=15552000; SameSite=Lax';
  var name = decodeURIComponent(location.hash.slice(1)) || 'map.sbgn';
  document.title = name + ' · Newt';
  var channel = new BroadcastChannel('newt-open'), text = null, started = Date.now();
  channel.onmessage = function (e) { if (e.data && e.data.key === key) text = e.data.text; };
  var wait = setInterval(function () {
    if (Date.now() - started > 30000) {  // the page that made the file was closed or reloaded
      clearInterval(wait); channel.close(); document.title = name + ' (no longer on its page) · Newt'; return;
    }
    if (text === null) { channel.postMessage({ ask: key }); return; }
    var input = window.$ && $('#file-input')[0];
    if (!window.cy || !input || !($._data(input, 'events') || {}).change) return;
    clearInterval(wait); channel.close();
    $(input).trigger('change', [new File([text], name, { type: 'text/plain' })]);
  }, 250);
})();
