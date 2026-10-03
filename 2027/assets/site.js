// ENG 511, Fall 2027. Finds the current week. The site reads in full without this script.
// Week 1 begins Monday, August 23, 2027. To test any week, add ?week=7 to the address.
(function () {
  var first = Date.UTC(2027, 7, 23);
  var now = new Date();
  var today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  var n = Math.floor((today - first) / 604800000) + 1;
  var state = 'now';
  var asked = null;
  try { asked = new URLSearchParams(window.location.search).get('week'); } catch (e) { asked = null; }
  if (asked && /^\d+$/.test(asked) && +asked >= 1 && +asked <= 16) { n = +asked; }
  else if (n < 1) { n = 1; state = 'before'; }
  else if (n > 16) { n = 16; state = 'after'; }

  var block = document.querySelector('[data-week-block="' + n + '"]');
  if (block) {
    block.hidden = false;
    var label = block.querySelector('[data-marker]');
    if (label && state === 'before') { label.textContent = 'First week · classes begin Tuesday, August 24'; }
    if (label && state === 'after') { label.textContent = 'Final week'; }
    var fallback = document.querySelector('[data-week-fallback]');
    if (fallback) { fallback.hidden = true; }
    document.title = 'Week ' + n + ' · ENG 511';
  }
  if (state !== 'now') { return; }
  var rows = document.querySelectorAll('tr[data-week="' + n + '"]');
  for (var i = 0; i < rows.length; i++) {
    rows[i].className += ' now';
    var cell = rows[i].querySelector('[data-week-cell]');
    if (cell) { cell.textContent = n + ', this week'; }
  }
  var marks = document.querySelectorAll('[data-this-week="' + n + '"]');
  for (var j = 0; j < marks.length; j++) { marks[j].hidden = false; }
})();
