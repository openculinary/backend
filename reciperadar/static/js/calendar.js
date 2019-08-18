function minDate() {
  var thisHour = moment().startOf('hour');
  return thisHour.add(1, 'hours');
}

function maxDate() {
  return minDate().add(1, 'month').endOf('day');
}

function defaultDate() {
  var today = moment().startOf('day');
  var endOfDay = today.add(17, 'hours');
  if (endOfDay < minDate()) endOfDay.add(1, 'day');
  return endOfDay;
}

$('#datetimepicker').datetimepicker({
  minDate: minDate(),
  maxDate: maxDate(),
  defaultDate: defaultDate(),
  inline: true,
  sideBySide: true,
  stepping: 5
});
$('#datetimepicker th[class^=picker]').removeAttr('data-action');
$('#datetimepicker th[class^=picker]').addClass('deactivated');
$('#datetimepicker span[class^=timepicker]').removeAttr('data-action');
$('#datetimepicker span[class^=timepicker]').addClass('deactivated');

$('#reminder').submit(function(e) { e.preventDefault(); });
