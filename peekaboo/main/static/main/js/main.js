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

  $(document).ajaxError(function(event, jqxhr, settings, exception) {
    var description = jqxhr.responseText;
    if (description === 'Forbidden') {
      description = "Un unauthorized data retrieval attempted happend. Are you logged in?";
    }
    Utils.ajax_error("AJAX Server Error", description);
  });

});
