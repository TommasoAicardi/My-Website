document.addEventListener('DOMContentLoaded', function () {
  var navLinks = document.querySelectorAll('.nav-link');
  var sections = document.querySelectorAll('.page-section');

  navLinks.forEach(function (link) {
    link.addEventListener('click', function () {
      var target = link.dataset.section;

      navLinks.forEach(function (l) {
        var isActive = l === link;
        l.classList.toggle('active', isActive);
        l.setAttribute('aria-selected', isActive);
      });

      sections.forEach(function (section) {
        section.hidden = section.id !== target;
      });
    });
  });

  var themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function () {
      var root = document.documentElement;
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  var paperList = document.getElementById('paper-list');
  if (paperList) {
    fetch(paperList.dataset.src)
      .then(function (response) {
        if (!response.ok) throw new Error('Failed to load papers.json');
        return response.json();
      })
      .then(function (papers) {
        if (!Array.isArray(papers) || papers.length === 0) {
          paperList.innerHTML = '<li class="paper-item paper-empty">No publications listed yet — check the Google Scholar profile above.</li>';
          return;
        }
        paperList.innerHTML = papers.map(function (paper) {
          var meta = [paper.authors, paper.venue, paper.year].filter(Boolean).join(' — ');
          var link = paper.link
            ? '<a href="' + encodeURI(paper.link) + '" target="_blank" rel="noopener">View ↗</a>'
            : '';
          return '<li class="paper-item">' +
            '<span class="item-title">' + escapeHtml(paper.title || 'Untitled') + '</span>' +
            '<span class="item-meta">' + escapeHtml(meta) + '</span>' +
            link +
            '</li>';
        }).join('');
      })
      .catch(function () {
        paperList.innerHTML = '<li class="paper-item paper-empty">Couldn\'t load publications automatically — see the Google Scholar profile above.</li>';
      });
  }
});
