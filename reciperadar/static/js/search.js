function titleFormatter(value, row, index) {
  var ingredientHtml = '<ul>';
  row.ingredients.forEach(function(ingredient) {
  ingredientHtml += '<li style="font-size: 13px"><div onclick="toggleIngredientState($(this))">' + ingredient.ingredient + '</div></li> ';
  });
  ingredientHtml += '</ul>'
  return '<img style="max-width: 24px" src="images/domains/' + row.domain + '.ico" alt="" />&nbsp;&nbsp;<a href="' + row.url + '">' + row.title + '</a><br /><br />' + ingredientHtml;
}

function imageFormatter(value, row, index) {
  var matchHtml = '<div style="width: 192px">';
  row.matches.forEach(function(match) {
    matchHtml += '<span class="tag badge badge-info">' + match + '</span> ';
  });
  $('#exclude').val().forEach(function(exclude) {
    matchHtml += '<span class="tag badge badge-info badge-exclude">no: ' + exclude + '</span> ';
  });
  return '</div><img style="max-width: 192px" src="' + value + '" alt="' + row.title + '"><hr />' + matchHtml;
}

function metadataFormatter(value, row, index) {
  var duration = moment.duration(row.time, 'minutes');
  return `
<table style="font-size: 12px">
  <tr>
    <th colspan="2">
      <span style="white-space: nowrap">
        <button class="btn btn-outline-success" aria-label="Add to calendar" data-toggle="modal" data-target="#calendarize" data-recipe-id="` + row.id + `"><img src="images/icons/calendar.svg" alt="" /></button>
        <button class="btn btn-outline-warning" aria-label="Share by email"><a href="mailto:?subject=` + row.title + `&body=` + row.url + `" aria-label="Share by email"><img src="images/icons/mail.svg" alt="" /></a></button>
        <button class="btn btn-outline-primary" aria-label="Copy to clipboard" data-clipboard-text="` + row.url + `"><img src="images/icons/link.svg" alt="" /></button>
      </span>
    </th>
  </tr>
  <tr><th>time</th><td>` + duration.as('minutes') + ` mins</td></tr>
</table>
`;
}

function pushSearch() {
  var state = {'action': 'search'};
  ['#include', '#exclude'].forEach(function (element) {
    var fragment = element.replace('#', '');
    var data = $(element).val();
    if (data.length > 0) {
      state[fragment] = data.join(',');
    }
  })
  // bbq merge mode 2: completely replace fragment state
  $.bbq.pushState(state, 2);
}

function executeSearch() {
  var params = {
    include: $('#include').val(),
    exclude: $('#exclude').val()
  };
  $('#recipes-container').removeClass('d-none');
  $('#recipes').bootstrapTable('refresh', {
    url: '/api/recipes/search?' + $.param(params),
    pageNumber: $.bbq.getState('page') || 1
  });
}
$('#search').click($.throttle(1000, true, pushSearch));

$('#recipes').on('page-change.bs.table', function(e, number, size) {
  $(window).off('hashchange').promise().then(function () {;
    if (number > 1) $.bbq.pushState({'page': number});
    else $.bbq.removeState('page');
  }).promise().then(function() {
    $(window).on('hashchange', loadState);
  });
});
$('#recipes').on('load-success.bs.table', function() {
  new ClipboardJS('#recipes .btn-outline-primary');
});
$('#calendarize').on('show.bs.modal', function (e) {
  var recipeId = $(e.relatedTarget).data('recipe-id');
  $('#calendarize').data('recipe-id', recipeId);
});

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
}

$(window).on('hashchange', loadState);
$(loadState);
