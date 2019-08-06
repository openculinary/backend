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
  switch (action) {
    case 'search': executeSearch(); break;
    case 'view': executeView(); break;
    default: $('#recipes-container').addClass('d-none');
  }
}

$(window).on('hashchange', loadState);
$(loadState);
