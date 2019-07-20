function bindIngredientInput(element, tagClass) {
  $(element).tagsinput({
    allowDuplicates: false,
    freeInput: false,
    maxTags: 20,
    tagClass: 'tag badge badge-info' + (tagClass ? ' ' + tagClass : ''),
    typeahead: {
      source: function(query, process) {
        if (query.length < 3) return true;
        return $.getJSON('api/ingredients?pre=' + query);
      },
      afterSelect: function() {
        this.$element[0].value = '';
      },
      sorter: function (item) { return item; }
    }
  });
}
bindIngredientInput('#include');
bindIngredientInput('#exclude', 'badge-exclude');
