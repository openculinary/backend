function bindShoppingListInput(element) {
  $(element).tagsinput({
    allowDuplicates: false,
    freeInput: false,
    itemText: 'raw',
    itemValue: 'singular',
    maxTags: 100,
    tagClass: function(item) {
      var state = item.state || 'required';
      if (Object.keys(item.recipes || {}).length) state += ' fixed';
      return 'badge badge-info ' + state;
    },
    typeahead: {
      minLength: 3,
      source: function(query) {
        return $.getJSON('api/ingredients', {pre: query});
      },
      afterSelect: function() {
        this.$element[0].value = '';
      }
    }
  });
  $(element).on('itemAdded', function(event) {
    var shoppingList = loadShoppingList();
    var product = event.item;
    addProductToShoppingList(shoppingList, product);
    storeShoppingList(shoppingList);

    var filter = 'span.tag.badge:contains("' + product.raw + '")';
    $('#shopping-list-input').off('click', filter);
    $('#shopping-list-input').on('click', filter, function () {
      // Workaround: filter ':contains' may return non-exact matches
      // i.e. contains('celery') -> ['celery', 'celery root', ...]
      if ($(this).text() != product.raw) return;
      toggleProductState(product.singular);
    });
  });
  $(element).on('beforeItemRemove', function(event) {
    var shoppingList = loadShoppingList();
    var product = shoppingList.products[event.item.singular];
    event.cancel = Object.keys(product.recipes).length;
    return;
  });
  $(element).on('itemRemoved', function(event) {
    var shoppingList = loadShoppingList();
    var product = shoppingList.products[event.item.singular];
    removeProductFromShoppingList(shoppingList, product);
    storeShoppingList(shoppingList);
  });
}
bindShoppingListInput('#shopping-list-add');

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
  $.each(shoppingList.recipes, function(recipeId) {
    var recipe = shoppingList.recipes[recipeId];
    var remove = $('<a />', {
      'class': 'remove fa fa-trash-alt',
      'click': removeRecipeFromShoppingList,
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

  var shoppingListInput = $('#shopping-list-add');
  shoppingListInput.tagsinput('removeAll');

  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    shoppingListInput.tagsinput('add', product);
  });
}

function addProductToShoppingList(shoppingList, product, recipeId) {
  if (!(product.singular in shoppingList.products)) {
    shoppingList.products[product.singular] = {
      raw: product.raw,
      singular: product.singular,
      plural: product.plural,
      state: product.state,
      recipes: {}
    }
  }

  if (!recipeId) return;
  shoppingList.products[product.singular].recipes[recipeId] = {};
}

function addRecipeToShoppingList(element) {
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
    if (product.state == 'required') {
      addProductToShoppingList(shoppingList, product, recipe.id);
    }
  });

  storeShoppingList(shoppingList);
  updateRecipeState(recipe.id);
  renderShoppingList();
}

function removeProductFromShoppingList(shoppingList, product, recipeId) {
  if (recipeId) delete product.recipes[recipeId];
  if (Object.keys(product.recipes).length) return;
  delete shoppingList.products[product.singular];
}

function removeRecipeFromShoppingList() {
  var shoppingList = loadShoppingList();

  var recipeId = $(this).data('recipe-id');
  delete shoppingList.recipes[recipeId];

  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    if (recipeId in product.recipes) {
      removeProductFromShoppingList(shoppingList, product, recipeId);
    }
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

function toggleProductState(productId) {
  var shoppingList = loadShoppingList();
  var product = shoppingList.products[productId];

  var transitions = {
    undefined: 'purchased',
    'available': 'purchased',
    'required': 'purchased',
    'purchased': 'required'
  };
  product.state = transitions[product.state];

  storeShoppingList(shoppingList);
  renderShoppingList();
}
