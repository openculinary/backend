function bindShoppingListInput(element) {
  $(element).tagsinput({
    freeInput: false,
    itemText: 'raw',
    itemValue: 'singular',
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
  $(element).on('beforeItemAdd', function(event) {
    event.cancel = true;

    var shoppingList = loadShoppingList();
    var product = event.item;
    if (product.singular in shoppingList.products) return;

    addProductToShoppingList(shoppingList, product);
    storeShoppingList(shoppingList);
    populateNotifications(shoppingList);

    var productsHtml = $('#shopping-list .products');
    productElement(product).appendTo(productsHtml);
  });
}
bindShoppingListInput('#shopping-list-entry');

function restoreShoppingList() {
  var data = $.bbq.getState('shopping-list');
  if (data) {
    $.getJSON('api/shopping-list/json.schema', function(schema) {
      var ajv = new Ajv({removeAdditional: true, useDefaults: true});
      var validate = ajv.compile(schema.reminder);
      data = base58.decode(data);
      data = pako.inflate(data);
      data = String.fromCharCode.apply(null, data);
      var shoppingList = JSON.parse(data);

      if (!validate(shoppingList)) return;
      storeShoppingList(shoppingList);
      renderShoppingList();
    });
  }
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

function recipeElement(recipe) {
  var remove = $('<a />', {
    'class': 'remove fa fa-trash-alt',
    'click': removeRecipeFromShoppingList,
    'data-recipe-id': recipe.id,
  });
  var title = $('<span />', {
    'class': 'recipe',
    'text': recipe.title
  });
  var item = $('<div />');

  remove.appendTo(item);
  title.appendTo(item);
  return item;
}

function aggregateUnitQuantities(product) {
  var unitQuantities = {};
  $.each(product.recipes, function(recipeId) {
    product.recipes[recipeId].amounts.forEach(function (amount) {
      if (!amount.units) amount.units = '';
      if (!(amount.units in unitQuantities)) unitQuantities[amount.units] = 0;
      unitQuantities[amount.units] += amount.quantity;
    });
  });
  $.each(unitQuantities, function(unit) {
    if (unitQuantities[unit] === 0) delete unitQuantities[unit];
  });
  return unitQuantities;
}

function renderProductText(product) {
  var unitQuantities = aggregateUnitQuantities(product);
  var productText = '';
  $.each(unitQuantities, function(unit) {
    if (productText) productText += ' + ';
    productText += float2rat(unitQuantities[unit]) + ' ' + unit;
  });
  productText += ' ' + product.raw;
  return productText;
}

function productElement(product) {
  var label = $('<label />', {
    'click': function() {
      toggleProductState(product.singular);
    }
  });
  $('<input />', {
    'type': 'checkbox',
    'name': 'products[]',
    'value': product.singular,
    'checked': product.state === 'purchased'
  }).appendTo(label);

  var productText = renderProductText(product);
  $('<span />', {'text': productText}).appendTo(label);

  if (Object.keys(product.recipes || {}).length === 0) {
    $('<span />', {
      'data-role': 'remove',
      'click': function() {
        var shoppingList = loadShoppingList();
        removeProductFromShoppingList(shoppingList, product);
        storeShoppingList(shoppingList);
        populateNotifications(shoppingList);
        $(this).parent().remove();
      }
    }).appendTo(label);
  }
  return label;
}

function populateNotifications(shoppingList) {
  var shoppingListEmpty = Object.keys(shoppingList.products).length == 0;
  $('header span.notification').toggle(!shoppingListEmpty);
  if (shoppingListEmpty) return;

  var total = 0, found = 0;
  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    total += 1;
    found += product.state === 'required' ? 0 : 1;
  });
  $('header span.notification').text(found + '/' + total);
}

function renderShoppingList() {
  var shoppingList = loadShoppingList();
  var shoppingListEmpty = Object.keys(shoppingList.products).length == 0;
  $('button[data-target="#reminder').prop('disabled', shoppingListEmpty);

  var recipesHtml = $('#shopping-list .recipes').empty();
  $.each(shoppingList.recipes, function(recipeId) {
    var recipe = shoppingList.recipes[recipeId];
    recipeElement(recipe).appendTo(recipesHtml);
  });

  var productsHtml = $('#shopping-list .products').empty();
  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    addProductToShoppingList(shoppingList, product);
    productElement(product).appendTo(productsHtml);
  });

  populateNotifications(shoppingList);
}

function addProductToShoppingList(shoppingList, product, recipeId) {
  if (!(product.singular in shoppingList.products)) {
    shoppingList.products[product.singular] = {
      raw: product.raw,
      singular: product.singular,
      plural: product.plural,
      state: product.state || 'required',
      recipes: {}
    }
  }

  if (!recipeId) return;
  var productRecipes = shoppingList.products[product.singular].recipes;
  if (!(recipeId in productRecipes)) {
    productRecipes[recipeId] = {amounts: []};
  }
  productRecipes[recipeId].amounts.push({
    quantity: product.quantity,
    units: product.units
  });
}

function addRecipeToShoppingList() {
  var recipe = {
    id: $(this).data('recipe-id'),
    title: $(this).data('recipe-title')
  };

  var shoppingList = loadShoppingList();
  shoppingList.recipes[recipe.id] = recipe;

  var products = $(this).data('products');
  $.each(products, function(productId) {
    var product = products[productId];
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
  var recipeId = $(this).data('recipe-id');

  var shoppingList = loadShoppingList();
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
