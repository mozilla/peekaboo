$(function() {
  $('ul.nav li').each(function() {
    if ($('a', this).attr('href') == location.pathname) {
      $(this).addClass('active');
    }
  });
});
