/* Every App Store link sends an Umami `app-store-click` event (the name the
   portfolio dash reads). Same pattern as getvelm.com: our own capture-phase
   listener, never Umami's data-umami-event attribute, whose handler calls
   preventDefault and navigates from script, so iOS Safari opens the App Store
   web page instead of the App Store app. umami.track posts with keepalive, so
   the event survives the navigation. A tap before the deferred Umami script
   has loaded isn't recorded: a slight undercount, never a broken hand-off. */
(() => {
  const placementFor = (link) => {
    if (link.dataset.where) return link.dataset.where;
    if (link.closest('footer')) return 'footer';
    return 'content';
  };
  document.addEventListener('click', (event) => {
    const link = event.target.closest && event.target.closest('a[href*="apps.apple.com/"]');
    if (!link) return;
    if (!window.umami || typeof window.umami.track !== 'function') return;
    window.umami.track('app-store-click', {
      page: window.location.pathname,
      placement: placementFor(link),
    });
  }, true);
})();
