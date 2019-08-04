function renderText(token) {
  return token.value;
}

function renderProduct(token) {
  return '<span class="tag badge ' + token.state + '" onclick="toggleIngredientState($(this))">' + token.value + '</span>'
}

function titleFormatter(value, row, index) {
  var ingredientHtml = '<ul>';
  row.ingredients.forEach(function(ingredient) {
    ingredientHtml += '<li style="font-size: 13px">';
    ingredient.tokens.forEach(function(token) {
      switch (token.type) {
        case 'text': ingredientHtml += renderText(token); break;
        case 'product': ingredientHtml += renderProduct(token); break;
      }
    });
    ingredientHtml += '</li>';
  });
  ingredientHtml += '</ul>'
  return '<img style="max-width: 24px" src="images/domains/' + row.domain + '.ico" alt="" />&nbsp;&nbsp;<a href="' + row.src + '">' + row.title + '</a><br /><br />' + ingredientHtml;
}

function imageFormatter(value, row, index) {
  return '<img style="max-width: 192px" src="' + value + '" alt="' + row.title + '">';
}

function metadataFormatter(value, row, index) {
  var duration = moment.duration(row.time, 'minutes');
  return `
<table class="metadata">
  <tr>
    <th colspan="2">
      <span>
        <button class="btn btn-outline-success" aria-label="Add to calendar" data-toggle="modal" data-target="#calendarize" data-recipe-id="` + row.id + `"><img src="images/icons/calendar.svg" alt="" /></button>
        <button class="btn btn-outline-warning" aria-label="Share by email"><a href="mailto:?subject=` + row.title + `&body=` + encodeURIComponent(window.location.origin + row.url) + `" aria-label="Share by email"><img src="images/icons/mail.svg" alt="" /></a></button>
        <button class="btn btn-outline-primary" aria-label="Copy to clipboard" data-clipboard-text="` + window.location.origin + row.url + `"><img src="images/icons/link.svg" alt="" /></button>
      </span>
    </th>
  </tr>
  <tr>
    <td><strong>time</strong></td>
    <td>` + duration.as('minutes') + ` mins</td>
  </tr>
</table>
`;
}

function scrollToSearchResults() {
  var scrollTop = $("#recipes-container").offset().top;
  $('html, body').animate({scrollTop: scrollTop}, 500);
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
  var sortChoice = $.bbq.getState('sort');
  if (sortChoice) state['sort'] = sortChoice;
  // bbq merge mode 2: completely replace fragment state
  $.bbq.pushState(state, 2);
}
$('#search').click($.throttle(1000, true, pushSearch));

function executeSearch() {
  var params = {
    include: $('#include').val(),
    exclude: $('#exclude').val()
  };
  var sortChoice = $.bbq.getState('sort');
  if (sortChoice) params['sort'] = sortChoice;
  $('#recipes').bootstrapTable('refresh', {
    url: '/api/recipes/search?' + $.param(params),
    pageNumber: Number($.bbq.getState('page') || 1)
  });
  $('#recipes-container').removeClass('d-none');
  scrollToSearchResults();
}

function executeView() {
  var id = $.bbq.getState('id');
  $('#recipes-container').removeClass('d-none');
  $('#recipes').bootstrapTable('refresh', {
    url: '/api/recipes/' + encodeURIComponent(id) + '/view'
  });
}

$('#recipes').on('page-change.bs.table', function(e, number, size) {
  $(window).off('hashchange').promise().then(function () {;
    if (number > 1) $.bbq.pushState({'page': number});
    else $.bbq.removeState('page');
    scrollToSearchResults();
  }).promise().then(function() {
    $(window).on('hashchange', loadState);
  });
});
$('#recipes').on('load-success.bs.table', function() {
  new ClipboardJS('#recipes .btn-outline-primary');
});
$('#recipes').on('load-success.bs.table', function() {
  var sortOptions = [
    {val: 'relevance', text: 'most relevant'},
    {val: 'ingredients', text: 'fewest extras required'},
    {val: 'duration', text: 'shortest time to make'},
  ];
  var sortChoice = $.bbq.getState('sort') || sortOptions[0].val;

  var sortSelect = $('<select>');
  $(sortOptions).each(function() {
    var sortOption = $('<option>');
    sortOption.text(this.text);
    sortOption.attr('value', this.val);
    if (sortChoice === this.val) sortOption.attr('selected', 'selected');
    sortSelect.append(sortOption);
  });
  sortSelect.on('change', function() {
    var sort = this.value;
    $(window).off('hashchange').promise().then(function () {
      $.bbq.removeState('page');
      $(window).on('hashchange', loadState).promise().then(function () {
        $.bbq.pushState({'sort': sort});
      });
    });
  });

  var sortPrompt = $('<span>').text('Order by ');
  sortSelect.appendTo(sortPrompt);

  var paginationDetail = $('#recipes-container div.pagination-detail');
  paginationDetail.empty();
  sortPrompt.appendTo(paginationDetail);
});
$('#calendarize').on('show.bs.modal', function (e) {
  var recipeId = $(e.relatedTarget).data('recipe-id');
  $('#calendarize').data('recipe-id', recipeId);
});
