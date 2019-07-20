$('#datetimepicker').datetimepicker({
  minDate: moment().format('YYYY-MM-DD'),
  defaultDate: moment().format('YYYY-MM-DD'),
  format: 'YYYY-MM-DD'
});

$('#calendarize form').submit(function(e) { e.preventDefault(); });
