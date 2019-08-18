function renderText(token) {
  return token.value;
}

function renderProduct(token) {
  return '<span class="tag badge ' + token.state + '">' + token.value + '</span>'
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
  var duration = moment.duration(row.time, 'minutes');
  var productsToAdd = [];
  row.ingredients.forEach(function(ingredient) {
    ingredient.tokens.forEach(function(token) {
      if (token.type == 'product') {
        productsToAdd.push({
          raw: token.value,
          singular: token.singular,
          plural: token.plural,
          state: token.state
	});
      }
    });
  });
  return `
<div class="metadata">
<img src="` + value + `" alt="` + row.title + `">
<span><strong>serves</strong></span>
<span>` + row.servings + `</span>
<br />
<span><strong>time</strong></span>
<span>` + duration.as('minutes') + ` mins</span>
<button class="btn btn-outline-primary" style="font-size: 12px; width: 192px" data-recipe-id="` + row.id + `" data-recipe-title="` + row.title + `" data-products='` + JSON.stringify(productsToAdd) + `' onclick="addRecipeToShoppingList($(this))">Add to shopping list</button>
</div>
`;
}

function scrollToSearchResults() {
  var scrollTop = $('#search div.results').offset().top - $('header').height() - 32;
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
$('#search button').click($.throttle(1000, true, pushSearch));

function executeSearch() {
  var params = {
    include: $('#include').val(),
    exclude: $('#exclude').val()
  };
  var sortChoice = $.bbq.getState('sort');
  if (sortChoice) params['sort'] = sortChoice;
  $('#search div.results table').bootstrapTable('refresh', {
    url: '/api/recipes/search?' + $.param(params),
    pageNumber: Number($.bbq.getState('page') || 1)
  });
  $('#search div.results').show();
  scrollToSearchResults();
}

function executeView() {
  var id = $.bbq.getState('id');
  $('#search div.results').show();
  $('#search div.results table').bootstrapTable('refresh', {
    url: '/api/recipes/' + encodeURIComponent(id) + '/view'
  });
}

$('#search div.results table').on('page-change.bs.table', function(e, number, size) {
  $(window).off('hashchange').promise().then(function () {;
    if (number > 1) $.bbq.pushState({'page': number});
    else $.bbq.removeState('page');
    scrollToSearchResults();
  }).promise().then(function() {
    $(window).on('hashchange', loadState);
  });
});

$('#search div.results table').on('load-success.bs.table', function() {
  var sortOptions = [
    {val: 'relevance', text: 'most relevant'},
    {val: 'ingredients', text: 'fewest extras required'},
    {val: 'duration', text: 'shortest time to make'},
  ];
  var sortChoice = $.bbq.getState('sort') || sortOptions[0].val;

  var sortSelect = $('<select>').attr('aria-label', 'Recipe sort selection');
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

  var paginationDetail = $('#search div.results div.pagination-detail');
  paginationDetail.empty();
  sortPrompt.appendTo(paginationDetail);
});

$('#search div.results table').on('post-body.bs.table', function(data) {
  var data = $(this).bootstrapTable('getData');
  if (!Array.isArray(data)) return;
  data.forEach(function (row) {
    updateRecipeState(row.id);
  });
});
