$(function() {
  $('#sidebar button.pullout').click(function () {
    $('#shopping-list-card').toggleClass('active');
  });
  $('#sidebar button.close').click(function () {
    $('#shopping-list-card').removeClass('active');
  });

  $('#shopping-list-card').swipe({
    swipe: function(event, direction, distance, duration, fingers, fingerData) {
      if (direction === 'left') $('#shopping-list-card').addClass('active');
      if (direction === 'right') $('#shopping-list-card').removeClass('active');
    }
  });

  renderShoppingList();
});

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
  if (Object.keys(shoppingList.recipes).length) {
    $('#sidebar').removeClass('d-none');
    $('#shopping-list-card').addClass('active');
  } else {
    $('#shopping-list-card').removeClass('active');
  }

  var recipeListHtml = $('<ul />');
  $.each(shoppingList.recipes, function(recipe) {
    var recipe = shoppingList.recipes[recipe];
    var remove = $('<a />', {
      'class': 'remove',
      'click': removeFromShoppingList,
      'data-recipe-id': recipe.id,
      'text': 'x'
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
        state: 'shopping-list',
        recipes: {}
      }
    }
    shoppingList.products[product.singular].recipes[recipe.id] = {};
  });

  storeShoppingList(shoppingList);
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
  renderShoppingList();
}

function toggleIngredientState() {
  var shoppingList = loadShoppingList();
  var productId = $(this).data('product-id');
  var product = shoppingList.products[productId];

  var transitions = {
    'shopping-list': 'purchased',
    'purchased': 'shopping-list'
  };
  product.state = transitions[product.state];

  storeShoppingList(shoppingList);
  renderShoppingList();
}
