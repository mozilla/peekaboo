var Log = (function() {
  var latest = null;

  function make_timeago($element) {
    var datetime = $element.attr('datetime');
    var format = $element.attr('data-format');
    var parsed = moment(datetime);
    $element.text(parsed.format(format));
    $element.timeago();
  }

  function add_rows(rows, highlight) {
    var parent = $('#entries');
    var template = $('#entry-template .entry');
    $('.new').removeClass('new');
    $.each(rows, function(i, row) {
      var copy = template.clone();
      if (highlight) {
        copy.addClass('new');
      }
      copy.data('id', row.id);
      copy.attr('id', 'entry-' + row.id);
      $('h3', copy).text(row.name);
      $('.company span', copy).text(row.company);
      $('.visiting span', copy).text(row.visiting);
      $('.visiting a', copy)
        .attr('href', 'mailto:' + row.email)
        .text(row.email);
      $('time', copy)
        .attr('datetime', row.modified_iso)
        .text(row.modified);
      copy.prependTo(parent);
      make_timeago($('time', copy));
    });
  }

  function getURL() {
    return location.pathname + 'entries/';
  }

  function fetch(highlight) {
    $.getJSON(getURL(), {latest: latest}, function(response) {
      if (response.latest) {
        latest = response.latest;
      }
      add_rows(response.rows, highlight);
    });
  }

  return {
    init: function() {
      fetch(false);
      setTimeout(function() {
        setInterval(function() {
          fetch(true);
        }, 10 * 1000);
      }, 10 * 1000);

      $('.entry button').on('click', function() {
        console.log('clicked!');
        return false;
      });
    }
  };
})();


$(function() {
  Log.init();
});
