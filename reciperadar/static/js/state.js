function loadTags(element, data) {
  $(element).tagsinput('removeAll');
  if (!data) return;
  data.split(',').forEach(function(tag) {
    $(element).tagsinput('add', tag);
  });
}

function loadState() {
  loadTags('#include', $.bbq.getState('include'));
  loadTags('#exclude', $.bbq.getState('exclude'));

  var action = $.bbq.getState('action');
  if (!action) $('#recipes-container').addClass('d-none');
  if (action == 'search') executeSearch();
  if (action == 'verified') confirmVerified();
}

$(window).on('hashchange', loadState);
$(loadState);
