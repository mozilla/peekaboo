$(function() {
  function toggle(href) {
    $('#tabs li.active').removeClass('active');
    if (href === '#expanded') {
      $('#stats-collapsed').hide();
      $('#stats-expanded').show(300);
    } else {
      $('#stats-expanded').hide();
      $('#stats-collapsed').show(300);
    }
    $('#tabs li').each(function() {
      if ($('a', this).attr('href') === href) {
        $(this).addClass('active');
      } else {
        $(this).removeClass('active');
      }
    });
  }
  $('#tabs li a').click(function() {
    toggle($(this).attr('href'));
  });
  if (location.hash === '#expanded' || location.hash === '#collapsed') {
    toggle(location.hash);
  }
});
