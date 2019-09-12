function loadMealPlan() {
  var mealPlanJSON = window.localStorage.getItem('mealPlan');
  var emptyMealPlanJSON = JSON.stringify({});
  return JSON.parse(mealPlanJSON || emptyMealPlanJSON);
}

function storeMealPlan(mealPlan) {
  var mealPlanJSON = JSON.stringify(mealPlan);
  window.localStorage.setItem('mealPlan', mealPlanJSON);

  var recipeCounts = {};
  $.each(mealPlan, function(date) {
    mealPlan[date].forEach(function (recipe) {
      if (!(recipe.id in recipeCounts)) recipeCounts[recipe.id] = 0;
      recipeCounts[recipe.id]++;
    });
  });

  var shoppingList = loadShoppingList();
  $.each(shoppingList.recipes, function(recipeId) {
    shoppingList.recipes[recipeId].multiple = recipeCounts[recipeId] || 1;
  });
  storeShoppingList(shoppingList);
  renderShoppingList(shoppingList);
}

function removeRecipeFromMealPlan() {
  var mealPlan = loadMealPlan();
  var recipeId = $(this).parents('.recipe').children('a').data('recipe-id');

  var date = $(this).parents('tr').data('date');
  var index = mealPlan[date].map(function(recipe) { return recipe.id; }).indexOf(recipeId);

  if (index >= 0) mealPlan[date].splice(index, 1);
  if (!mealPlan[date].length) delete mealPlan[date];

  $(this).parents('.recipe').remove();
  storeMealPlan(mealPlan);
}

function cloneHandler(evt) {
  var elements = [evt.item, evt.clone];
  elements.forEach(function (element) {
    var shoppingListRemove = $(element).find('a.remove');
    shoppingListRemove.off('click');
    shoppingListRemove.on('click', removeRecipeFromShoppingList);

    var mealPlanRemove = $(element).find('span[data-role="remove"]');
    mealPlanRemove.off('click');
    mealPlanRemove.on('click', removeRecipeFromMealPlan);
  });
}

function endHandler(evt) {
  var mealPlan = loadMealPlan();
  var recipeId = $(evt.item).children('a').data('recipe-id');

  var fromRow = $(evt.from).parents('tr');
  if (fromRow.length) {
    var date = fromRow.data('date');
    var index = mealPlan[date].map(function(recipe) { return recipe.id; }).indexOf(recipeId)

    if (index >= 0) mealPlan[date].splice(index, 1);
    if (!mealPlan[date].length) delete mealPlan[date];
  }

  var toRow = $(evt.to).parents('tr');
  var date = toRow.data('date');

  if (!(date in mealPlan)) mealPlan[date] = [];
  mealPlan[date].push({id: recipeId});

  storeMealPlan(mealPlan);
}

$(function() {
  $('#meal-planner .recipes').each(function(index, element) {
    new Sortable(element, {
      group: {
        name: 'meal-planner',
        pull: 'clone',
        put: false
      },
      sort: false,
      onClone: cloneHandler,
      onEnd: endHandler
    });
  });

  var mealPlan = loadMealPlan();
  var shoppingList = loadShoppingList();

  var idxDate = defaultDate();
  var endDate = defaultDate().add(1, 'week');
  var scheduler = $('#meal-planner table');
  for (; idxDate < endDate; idxDate.add(1, 'day')) {
    var date = idxDate.format('YYYY-MM-DD');
    var day = idxDate.format('dddd');

    var row = $('<tr />', {'data-date': date});
    var header = $('<th />', {'text': day});
    var cell = $('<td />');

    if (date in mealPlan) {
      $.each(mealPlan[date], function (index, recipe) {
        if (!(recipe.id in shoppingList.recipes)) return;
        var recipe = shoppingList.recipes[recipe.id];
        var element = recipeElement(recipe);
        cell.append(element);
      });
    }

    row.append(header);
    row.append(cell);
    scheduler.append(row);
  }

  $('#meal-planner td').each(function(index, element) {
    new Sortable(element, {
      group: {
        name: 'meal-planner'
      },
      onEnd: endHandler
    });
  });
});
