function bindShoppingListInput(element) {
  $(element).tagsinput({
    freeInput: false,
    itemText: 'product',
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
    renderShoppingList(shoppingList);
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
      renderShoppingList(shoppingList);
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
  var remove = $('<a />', {'class': 'remove fa fa-trash-alt'});
  remove.on('click', removeRecipeFromShoppingList);
  remove.on('click', removeRecipeFromMealPlan);

  var title = $('<span />', {
    'class': 'tag badge badge-info',
    'text': recipe.title
  });
  var cloneRemove = $('<span />', {
    'click': removeMealFromMealPlan,
    'data-role': 'remove'
  });
  var item = $('<div />', {
    'class': 'recipe',
    'data-id': recipe.id,
    'data-title': recipe.title
  });

  remove.appendTo(item);
  cloneRemove.appendTo(title);
  title.appendTo(item);
  return item;
}

function aggregateUnitQuantities(product) {
  var shoppingList = loadShoppingList();
  var unitQuantities = {};
  $.each(product.recipes, function(recipeId) {
    var multiple = shoppingList.recipes[recipeId].multiple || 1;
    product.recipes[recipeId].amounts.forEach(function (amount) {
      if (!amount.units) amount.units = '';
      if (!(amount.units in unitQuantities)) unitQuantities[amount.units] = 0;
      unitQuantities[amount.units] += amount.quantity * multiple;
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
  productText += ' ' + product.product;
  return productText;
}

function categoryElement(category) {
  category = category || 'Other';
  var fieldset = $('<fieldset />', {'class': category.toLowerCase()});
  $('<legend />', {'text': category}).appendTo(fieldset);
  return fieldset;
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
    'checked': ['available', 'purchased'].includes(product.state)
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
        renderShoppingList(shoppingList);
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

function updateReminderState(shoppingList) {
  var shoppingListEmpty = Object.keys(shoppingList.products).length == 0;
  $('button[data-target="#reminder').prop('disabled', shoppingListEmpty);
}

function getProductsByCategory(shoppingList) {
  var categoriesByProduct = {};
  $.each(shoppingList.products, function(productId) {
    categoriesByProduct[productId] = shoppingList.products[productId].category;
  });
  var productsByCategory = {};
  $.each(categoriesByProduct, function(productId) {
    var category = categoriesByProduct[productId];
    if (!(category in productsByCategory)) productsByCategory[category] = [];
    productsByCategory[category].push(productId);
  });
  return productsByCategory;
}

function renderShoppingList(shoppingList) {
  var recipesHtml = $('#meal-planner .recipes').empty();
  $.each(shoppingList.recipes, function(recipeId) {
    var recipe = shoppingList.recipes[recipeId];
    recipeElement(recipe).appendTo(recipesHtml);
  });

  var productsHtml = $('#shopping-list .products').empty();
  var finalCategoryGroup = null;
  var productsByCategory = getProductsByCategory(shoppingList);
  $.each(productsByCategory, function(category) {
    if (category === 'null') category = null;
    var categoryGroup = categoryElement(category);
    productsByCategory[category].forEach(function(productId) {
      var product = shoppingList.products[productId];
      productElement(product).appendTo(categoryGroup);
    });
    if (category) categoryGroup.appendTo(productsHtml);
    else finalCategoryGroup = categoryGroup;
  });
  if (finalCategoryGroup) finalCategoryGroup.appendTo(productsHtml);

  populateNotifications(shoppingList);
  updateReminderState(shoppingList);
}

function addProductToShoppingList(shoppingList, product, recipeId) {
  if (!(product.singular in shoppingList.products)) {
    shoppingList.products[product.singular] = {
      product: product.product,
      category: product.category,
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
  var shoppingList = loadShoppingList();

  var recipe = getRecipe(this);
  shoppingList.recipes[recipe.id] = {
    id: recipe.id,
    title: recipe.title,
    multiple: 1
  };

  $.each(recipe.products, function(productId) {
    var product = recipe.products[productId];
    addProductToShoppingList(shoppingList, product, recipe.id);
  });
  updateRecipeState(recipe.id, shoppingList);

  storeShoppingList(shoppingList);
  renderShoppingList(shoppingList);
}

function removeProductFromShoppingList(shoppingList, product, recipeId) {
  if (recipeId) delete product.recipes[recipeId];
  if (Object.keys(product.recipes).length) return;
  delete shoppingList.products[product.singular];
}

function removeRecipeFromShoppingList() {
  var shoppingList = loadShoppingList();

  var recipe = getRecipe(this);
  delete shoppingList.recipes[recipe.id];

  $.each(shoppingList.products, function(productId) {
    var product = shoppingList.products[productId];
    if (recipe.id in product.recipes) {
      removeProductFromShoppingList(shoppingList, product, recipe.id);
    }
  });
  updateRecipeState(recipe.id, shoppingList);

  storeShoppingList(shoppingList);
  renderShoppingList(shoppingList);
}

function updateRecipeState(recipeId, shoppingList) {
  var addButton = $(`#search .results .recipe[data-id="${recipeId}"] button.add-to-shopping-list`);
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
  renderShoppingList(shoppingList);
}

$(function () {
  var shoppingList = loadShoppingList();
  renderShoppingList(shoppingList);
});
