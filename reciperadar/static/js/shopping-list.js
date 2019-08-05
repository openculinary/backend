$(function() {
  $('#shopping-list-toggle').click(function () {
    $('#shopping-list-card').toggleClass('active');
  });

  $('#shopping-list-card').swipe({
    swipe: function(event, direction, distance, duration, fingers, fingerData) {
      if (direction === 'right') $('#shopping-list-card').removeClass('active');
    }
  });

  renderShoppingList();
});

function loadShoppingList() {
  var productsJSON = window.localStorage.getItem('shoppingList.products');
  return JSON.parse(productsJSON || '{}');
}

function storeShoppingList(products) {
  var productsJSON = JSON.stringify(products);
  window.localStorage.setItem('shoppingList.products', productsJSON);
}

function renderShoppingList() {
  var products = loadShoppingList();
  var shoppingList = $('#shopping-list').empty();
  $.each(products, function(product) {
    var product = products[product];
    $('<span />', {
      class: 'tag badge badge-info shopping-list',
      click: toggleIngredientState,
      text: product.raw
    }).appendTo($('<li />').appendTo(shoppingList));
  });
  highlightSearchResults();
}

function highlightSearchResults() {
  var products = loadShoppingList();
  $.each(products, function(product) {
    var product = products[product];
    $('span.tag:contains(' + product.singular + ')').addClass('shopping-list');
    $('span.tag:contains(' + product.plural + ')').addClass('shopping-list');
  });
}
$('#recipes').on('load-success.bs.table', highlightSearchResults);

function addToShoppingList(element) {
  var products = loadShoppingList();
  var productsToAdd = element.data('products');
  productsToAdd.forEach(function(product) {
    if (product.singular in products) return;
    products[product.singular] = {
      raw: product.raw,
      singular: product.singular,
      plural: product.plural
    };
  });
  storeShoppingList(products);
  renderShoppingList();
}

function toggleIngredientState() {
  $(this).toggleClass('purchased');
}
