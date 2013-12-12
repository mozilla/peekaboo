var Utils = (function() {
  return {
    ajax_error: function(msg, description, callback) {
      var $modal = $('#ajax-error-modal');
      $('h3', $modal).text(msg);
      if (description) {
        $('.description', $modal).text(description);
      } else {
        $('.description', $modal).text($('.description', $modal).data('default'));
      }
      $modal.modal();  // yuck!
      if (callback) {
        callback();
      }
    }
  };
})();


$(function() {
  $('ul.nav li').each(function() {
    if ($('a', this).attr('href') == location.pathname) {
      $(this).addClass('active');
    }
  });

});
