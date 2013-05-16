var Log = (function() {
  var latest = null;

  function make_timeago($element) {
    var datetime = $element.attr('datetime');
    var format = $element.attr('data-format');
    var parsed = moment(datetime);
    $element.text(parsed.format(format));
    $element.timeago();
  }

  function open_edit_entry(id) {
    var url = getURL(id);
    $('#edit-entry form')
      .attr('action', url)
      .data('id', id);
    $.getJSON(url, function(response) {
      var container = $('#edit-entry');
      $.each(response, function(key, value) {
        $('[name="' + key + '"]', container).val(value);
      });
      container.modal();
    });
  }

  function open_print_entry(id) {
    var url = getPrintURL(id);
    open(url);
  }

  function submit_edit_entry(event) {
    var $form = $(this);
    $.post($form.attr('action'), $form.serializeObject(), function(response) {
      var $entry = $('#entry-' + $form.data('id'));
      _fill_row_data($entry, response);
      $entry.addClass('new');
      $('#edit-entry').modal('hide');
    });
    return false;
  }

  function add_rows(rows, highlight) {
    var parent = $('#entries');
    var template = $('#entry-template .entry');
    $.each(rows, function(i, row) {
      var copy = template.clone();
      if (highlight) {
        copy.addClass('new');
        setTimeout(function() {
          $('.new').removeClass('new');
        }, 3 * 1000);
      }
      copy.data('id', row.id);
      copy.attr('id', 'entry-' + row.id);
      _fill_row_data(copy, row);
      $('button.edit', copy).on('click', function() {
        open_edit_entry($(this).parents('.entry').data('id'));
        return false;
      });
      $('button.print', copy).on('click', function() {
        open_print_entry($(this).parents('.entry').data('id'));
        return false;
      });
      $('button.delete', copy).on('click', function() {
        $('.delete-confirmation').hide();
        var parent = $(this).parents('.entry');
        $('.delete-confirmation', parent).show();
        return false;
      });
      $('button.delete-confirm', copy).on('click', function() {
        var $form = $('#delete-entry form');
        var $parent = $(this).parents('.entry');
        var id = $parent.data('id');
        $('input[name="id"]', $form).val(id);
        var url = getURL(id, true);
        $.post(url, $form.serializeObject(), function(response) {
          $parent.fadeOut(400);
        });
        return false;
      });
      $('button.delete-cancel', copy).on('click', function() {
        var parent = $(this).parents('.entry');
        $('.delete-confirmation', parent).hide();
        return false;
      });
      copy.prependTo(parent);
      make_timeago($('time', copy));
    });
  }

  function modify_rows(rows, highlight) {
    $.each(rows, function(i, row) {
      var entry = $('#entry-' + row.id);
      if (highlight) {
        entry.addClass('new');
        setTimeout(function() {
          $('.new').removeClass('new');
        }, 3 * 1000);
      }
      _fill_row_data(entry, row);
      make_timeago($('time', entry));
    });
  }

  function toggle_show_confirmation(element) {
  }

  function _fill_row_data(container, data) {
    $('.name', container).text(data.name);
    $('.job_title', container).text(data.job_title);
    $('.company', container).text(data.company);
    $('.visiting', container).text(data.visiting);
    $('.email a', container)
      .attr('href', 'mailto:' + data.email)
      .text(data.email);
    $('time', container)
      .attr('datetime', data.created_iso)
      .text(data.created);
    if (data.thumbnail) {
      $('img', container)
        .attr('src', data.thumbnail.url)
        .attr('width', data.thumbnail.width)
        .attr('height', data.thumbnail.height)
        .attr('alt', data.name);
    } else {
      $('img', container).hide();
    }
  }

  function getURL(id, delete_, print) {
    var locale = location.pathname.split('/')[1];
    var location_ = location.pathname.split('/')[3];
    var start = '/' + locale + '/log/' ;
    if (id) {
      if (delete_) {
        return start + 'entry/' + id + '/delete/';
      } else if (print) {
        //return start + 'entry/' + id + '/print/';
        return start + 'entry/' + id + '/print.pdf';
      } else {
        return start + 'entry/' + id + '/';
      }
    }
    return start + location_ + '/entries/';
  }

  function getPrintURL(id) {
    return getURL(id, false, true);
  }

  function fetch(highlight) {
    $.getJSON(getURL(), {latest: latest}, function(response) {
      if (response.latest) {
        latest = response.latest;
      }
      add_rows(response.created, highlight);
      modify_rows(response.modified, highlight);
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
      $('#edit-entry form').submit(submit_edit_entry);
    }
  };
})();


$.fn.serializeObject = function() {
  var o = {};
  var a = this.serializeArray();
  $.each(a, function() {
    if (o[this.name] !== undefined) {
      if (!o[this.name].push) {
        o[this.name] = [o[this.name]];
      }
      o[this.name].push(this.value || '');
    } else {
      o[this.name] = this.value || '';
    }
  });
  return o;
};


$(function() {
  Log.init();
});
