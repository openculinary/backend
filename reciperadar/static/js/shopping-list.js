$(function() {
  $('#shopping-list button.toggle').click(function () {
    $('#shopping-list').toggleClass('active');
    $(this).blur();
  });

  $('#shopping-list').swipe({
    swipeLeft: function() { $('#shopping-list').addClass('active'); },
    swipeRight: function() { $('#shopping-list').removeClass('active'); }
  });

  renderShoppingList();
});

function restoreShoppingList() {
  $.getJSON('api/shopping-list/json.schema', function(schema) {
    var ajv = new Ajv({removeAdditional: true, useDefaults: true});
    var validate = ajv.compile(schema.reminder);
    var data = $.bbq.getState('shopping-list');
    data = base58.decode(data);
    data = pako.inflate(data);
    data = String.fromCharCode.apply(null, data);
    var shoppingList = JSON.parse(data);

    if (!validate(shoppingList)) return;
    storeShoppingList(shoppingList);
    renderShoppingList();
  });
}

function loadShoppingList() {
  var shoppingListJSON = window.localStorage.getItem('shoppingList');
  var emptyShoppingListJSON = JSON.stringify({
    products: {},
    recipes: {}
  });
  return JSON.parse(shoppingListJSON || emptyShoppingListJSON);
}

function storeShoppingList(shoppingList) {
  var shoppingListJSON = JSON.stringify(shoppingList);
  window.localStorage.setItem('shoppingList', shoppingListJSON);
}

function renderShoppingList() {
  var shoppingList = loadShoppingList();
  if (Object.keys(shoppingList.products).length) {
    $('#shopping-list').removeClass('d-none');
    $('#shopping-list').addClass('active');
    $('button[data-target="#calendarize"]').prop('disabled', false);
  } else {
    $('#shopping-list').removeClass('active');
    $('button[data-target="#calendarize"]').prop('disabled', true);
  }

  var recipeListHtml = $('<ul />');
  $.each(shoppingList.recipes, function(recipe) {
    var recipe = shoppingList.recipes[recipe];
    var remove = $('<a />', {
      'class': 'remove fa fa-trash-alt',
      'click': removeFromShoppingList,
      'data-recipe-id': recipe.id,
    });
    var title = $('<span />', {
      'class': 'recipe',
      'text': recipe.title
    });
    var item = $('<li />');

    remove.appendTo(item);
    title.appendTo(item);
    item.appendTo(recipeListHtml);
  });
  var recipesHtml = $('#shopping-list-recipes').empty();
  recipeListHtml.appendTo(recipesHtml);

  var productListHtml = $('<ul />');
  $.each(shoppingList.products, function(product) {
    var product = shoppingList.products[product];
    $('<span />', {
      'class': 'tag badge badge-info ' + product.state,
      'click': toggleIngredientState,
      'data-product-id': product.singular,
      'text': product.raw
    }).appendTo($('<li />').appendTo(productListHtml));
  });
  var productsHtml = $('#shopping-list-products').empty();
  productListHtml.appendTo(productsHtml);
}

function addToShoppingList(element) {
  var shoppingList = loadShoppingList();

  var recipe = {
    id: element.data('recipe-id'),
    title: element.data('recipe-title')
  };
  if (!(recipe.id in shoppingList.recipes)) {
    shoppingList.recipes[recipe.id] = recipe;
  }

  var products = element.data('products');
  products.forEach(function(product) {
    if (!(product.singular in shoppingList.products)) {
      shoppingList.products[product.singular] = {
        raw: product.raw,
        singular: product.singular,
        plural: product.plural,
        state: product.state,
        recipes: {}
      }
    }
    shoppingList.products[product.singular].recipes[recipe.id] = {};
  });

  storeShoppingList(shoppingList);
  updateRecipeState(recipe.id);
  renderShoppingList();
}

function removeFromShoppingList() {
  var shoppingList = loadShoppingList();

  var recipeId = $(this).data('recipe-id');
  delete shoppingList.recipes[recipeId];

  var productsToRemove = [];
  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    delete product.recipes[recipeId];
    if (!Object.keys(product.recipes).length) productsToRemove.push(productId);
  });

  productsToRemove.forEach(function(productId) {
    delete shoppingList.products[productId];
  });

  storeShoppingList(shoppingList);
  updateRecipeState(recipeId);
  renderShoppingList();
}

function updateRecipeState(recipeId) {
  var shoppingList = loadShoppingList();
  var addButton = $('button[data-recipe-id="' + recipeId + '"]');
  var isInShoppingList = recipeId in shoppingList.recipes;
  addButton.prop('disabled', isInShoppingList);
  addButton.toggleClass('btn-outline-primary', !isInShoppingList);
  addButton.toggleClass('btn-outline-secondary', isInShoppingList);
}

function toggleIngredientState() {
  var shoppingList = loadShoppingList();
  var productId = $(this).data('product-id');
  var product = shoppingList.products[productId];

  var transitions = {
    'available': 'purchased',
    'required': 'purchased',
    'purchased': 'required'
  };
  product.state = transitions[product.state];

  storeShoppingList(shoppingList);
  renderShoppingList();
}
