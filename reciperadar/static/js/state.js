function loadTags(element, data) {
  if (!data) return;
  var tags = $(element).val();
  var terms = data.split(',');
  tags.forEach(function(tag) {
    if (terms.indexOf(tag) >= 0) return;
    $(element).tagsinput('remove', tag);
  });
  terms.forEach(function(term) {
    if (tags.indexOf(term) >= 0) return;
    $(element).tagsinput('add', {product: term, singular: term});
  });
}

function loadPage(pageId) {
  $('body > div.container[id]').hide();
  $('body > div.container[id="' + pageId + '"]').show();

  $('header a').removeClass('active');
  $('header a[href="#' + pageId + '"]').addClass('active');
}

function loadState() {
  loadTags('#include', $.bbq.getState('include'));
  loadTags('#exclude', $.bbq.getState('exclude'));

  $('body > div.container[id]').each(function() {
    if (this.id in $.bbq.getState()) loadPage(this.id);
  });

  var action = $.bbq.getState('action');
  switch (action) {
    case 'search': executeSearch(); break;
    case 'shopping-list': restoreShoppingList(); break;
    case 'verified': confirmVerified(); break;
    case 'view': executeView(); break;
  }
  renderShoppingList();
}

$(window).on('hashchange', loadState);
$(loadState);
