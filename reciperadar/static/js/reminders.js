function confirmVerified() {
  alert('Thank you!  Your email address has been verified.');
}

function sendReminder() {
  if (!$('#email')[0].checkValidity()) return;

  var dt = $('#datetimepicker').datetimepicker('date').format();
  var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  var email = $('#email').val();

  var url = '/api/shopping-list/reminder?' + $.param({
    'dt': dt,
    'tz': tz,
    'email': [encodeURIComponent(email)]
  });

  var shoppingList = JSON.stringify(loadShoppingList());
  $.post({
    url: url,
    contentType: 'application/json',
    data: shoppingList
  })
    .done(function() {
      $('#calendarize').modal('toggle');
    })
    .fail(function(xhr, status, error) {
      var response = $.parseJSON(xhr.responseText);
      if (!response) return;

      if (response.error === 'invalid_email') {
        var emailControl = $('#email')[0];
        emailControl.setCustomValidity('That email address seems invalid to us - please check and try again');
        emailControl.reportValidity();
      }
      if (response.error === 'unregistered_email') {
        $.post('/api/emails/register', {email: encodeURIComponent(email)});
        alert('Check your email inbox for an invitation, then try again');
      }
      if (response.error === 'unverified_email') {
        alert('Check your email inbox for an invitation, then try again');
      }
    });
}
$('#email').keyup(function(e) { $(this)[0].setCustomValidity(''); });
$('#reminder').click($.throttle(2500, true, sendReminder));
