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
    $(element).tagsinput('add', {raw: term, singular: term});
  });
}

function loadState() {
  loadTags('#include', $.bbq.getState('include'));
  loadTags('#exclude', $.bbq.getState('exclude'));

  var action = $.bbq.getState('action');
  switch (action) {
    case 'search': executeSearch(); break;
    case 'shopping-list': restoreShoppingList(); break;
    case 'verified': confirmVerified(); break;
    case 'view': executeView(); break;
    default: $('#recipes-container').addClass('d-none');
  }
}

$(window).on('hashchange', loadState);
$(loadState);
