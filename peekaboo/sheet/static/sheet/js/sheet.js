/*
setTimeout(function() {
$('.flash').addClass('fadeout');
}, 3000);
 */

var loader = null;

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

var Utils = (function() {
  return {
    showPanel: function(panel) {
      var currentPanel = document.getElementById(panel);
      window.location.hash = '#' + panel;
      SignIn.opened('#' + panel);
      /*
      currentPanel.addEventListener('transitionend', function() {
        SignIn.opened('#' + panel);
      });
      */
    },
    setActiveStep: function (step) {
      var menuBar = $('.menu-bar'),
          menuItems = menuBar.find('li');

      // Remove active from all items
      menuItems.each(function() {
        $(this).removeClass('active');
      });

      // Set the correct step as active
      $(step).addClass('active');
    },
    general_error: function(msg, reload_tip) {
      alert(msg);
    },
    ajax_error: function(msg, description, callback) {
      console.log(msg);
      console.log(description);
      $('#error h3').text(msg);
      if (description) {
        $('#error .description').text(description);
      } else {
        $('#error .description').text($('#error .description').data('default'));
      }
      //$('#error').modal();
      $('#error').show();
      if (callback) {
        callback();
      }
    }
  };
})();

var Config = (function() {
  // XXX could set up a cache here
  return {
    get: function(key) {
      return $('body').data('config-' + key);
    },
    set: function(key, value) {
      $('body').data('config-' + key, value);
    }
  };
})();


var SignIn = (function() {
  //var current_file;// deprecated?
  var _auto_reset_timer = null;
  var _photobooth_setup = false;
  //var snap_data_url = null;
  var snap_blob = null;

  // Because of https://bugzilla.mozilla.org/show_bug.cgi?id=1142123 if you
  // use a USB webcamera, you can't leave it "Always Share" because when
  // to start the stream the next time it goes back to the default camera
  // instead. So we leave in this hack to disable the stream being always on.
  var stream_always_on = !!localStorage.getItem('stream-always-on');
  if (stream_always_on) {
    console.warn(
      "NOTE! you have a localStorage key 'stream-always-on' " +
      "which means it will never stop the webcamera stream in " +
      "between panels.");
    console.log("To disable, type in:");
    console.log("localStorage.removeItem('stream-always-on')");
  }


  function opened(id) {
    /* Called when a pane is opened */

    if (id === '#thankyou') {
      _auto_reset_timer = setTimeout(function() {
        reset_all();
      }, 15 * 1000);
    } else if (id === '#signin') {
      if (_auto_reset_timer) {
        // just to be safe
        clearTimeout(_auto_reset_timer);
      }
    }

  }

  var was_group_signin = false;
  var stream_started = false;

  function submit($form, group_signin) {
    var location_id = Location.get_current_location().id;
    if (!location_id) {
      Utils.showPanel('location');
      return;
    }
    if (group_signin && !$('#id_company').val()) {
      Utils.general_error("Enter a Company name");
      return;
    }

    if (was_group_signin && !group_signin) {
      // You clicked the "Done" button.
      // This can mean two things, either you've just entered the last
      // person and want to submit that. Or you previously entered the last
      // person and now is ready to finish.
      // Basically, in this scenario, if no name has been entered exit out.
      if (!($('input[name="first_name"]', $form).val() || $('input[name="last_name"]', $form).val())) {
        reset_all();
        return;
      }
    }

    function setupCallback(camera_started) {
      if (camera_started) {
        $('div.photobooth.loading-canvas').hide();
        $('canvas.photobooth').show();
        // $('canvas.photobooth').show();
        $('#photobooth_container p.buttons').show();
        stream_started = true;
      } else {
        $('div.photobooth.loading-canvas').show();
        $('canvas.photobooth').hide();
        $('#photobooth_container').show();
        $('#photobooth_container p.buttons').hide();
        Utils.showPanel('picture');
        Utils.setActiveStep('#step_picture');
        $('#picture').fadeIn(300);
      }
    }

    var company = $('#id_company').val();
    var visiting = $('#id_visiting').val();

    $('#id_location', $form).val(location_id);
    $.post($form.attr('action'), $form.serializeObject(), function(response) {
        if (response.errors) {
          $.each(response.errors, function(key, errors) {
            if (key === '__all__') {
              Utils.general_error(errors.join('<br>'));
            } else {
              var $input = $('[name="' + key + '"]', form);
              $input
                .parents('.control-group')
                .addClass('error');
              $input.on('change', function() {
                $(this).parents('.error').removeClass('error');
                $('.help-inline', $(this).parents('.controls')).remove();
              });
              var $controls = $input.parents('.controls');
              $('.help-inline', $controls).remove();
              $('<span class="help-inline">')
                .text(errors.join(' '))
                .appendTo($controls);
            }
          });

        } else {
          $form[0].reset();
          if (group_signin) {
            $('#id_company').val(company);
            $('#id_visiting').val(visiting);
            setTimeout(function() {
              $('#id_first_name').focus();
            }, 100);
          }

          // If the form submission was a success,
          // at this point, we want to offer the user
          // the option to start over.
          $('.restart').show();

          $('.yourname').text(response.name);


          if (group_signin) {
            $('.individual', $form).hide();
            $('.group', $form).show();
          } else if (was_group_signin) {
            // XXX we could potentially summarize all the group logged in here
            $('.individual', $form).show();
            $('.group', $form).hide();
          } else {
            if (Config.get('take-picture')) {
              // make the canvas visible
              $('#picture').data('id', response.id);
              // console.log(stream_always_on, stream_started);
              if (stream_always_on && stream_started) {
                setupCallback(false);
                setupCallback(true);
              } else {
                Photobooth.setup(setupCallback);
              }

            } else {
              Utils.showPanel('thankyou');
              Utils.setActiveStep('#step_thankyou');
            }
          }

        }
      was_group_signin = group_signin;
    });
  }

  function upload_current_file(image, csrfmiddlewaretoken, callback) {
    var fd = new FormData();
    fd.append('picture', image);
    fd.append('csrfmiddlewaretoken', csrfmiddlewaretoken);
    var canvas_width = $('#photobooth_container canvas').attr('width');
    if (!canvas_width) {
      console.warn('Unable to read canvas width. Defaulting to 640');
      canvas_width = '640';
    }
    fd.append('thumbnail_geometry', canvas_width);
    $.ajax({
      url: 'upload/' + $('#picture').data('id') + '/',
      type: 'POST',
      data: fd,
      cache: false,
      contentType: false,
      processData: false,
      success: callback
    });
  }

  function reset_all() {
    var $form = $('#signin form');
    was_group_signin = false;
    $('.individual', $form).show();
    $('.group', $form).hide();
    $form[0].reset();
    $('.yourname').text('');
    $('.preview').hide();
    $('.restart').hide();
    $('.uploading').hide();
    if (Config.get('take-picture')) {
      $('#picture form').show();
    }
    $('.preview').hide();

    Utils.showPanel('signin');
    Utils.setActiveStep('step_signup');

    if (_auto_reset_timer) {
      clearTimeout(_auto_reset_timer);
    }
  }

  return {
    init: function() {

      // in case the browser caches any input fields
      $('#signin form')[0].reset();

      $('a.restart').click(function() {
        reset_all();
        return false;
      });

      $('#signin form').submit(function() {
        submit($(this), false);
        return false;
      });

      $('#signin button.group_signin').click(function() {
        submit($('#signin form'), true);
        return false;
      });

      $('#picture .proceed').click(function() {
        $('#picture .uploading').show();
        var csrfmiddlewaretoken = $('#picture input[name="csrfmiddlewaretoken"]').val();
        upload_current_file(snap_blob, csrfmiddlewaretoken, function(response) {
          if (response.errors) {
            Utils.general_error(response.errors);
          } else {
            if (response.thumbnail) {
              $('#thankyou .thumbnail')
                .attr('src', response.thumbnail.url)
                .attr('width', response.thumbnail.width)
                .attr('height', response.thumbnail.height);
              $('#thankyou .thumbnail').show();
            } else {
              $('#thankyou .thumbnail').hide();
            }
            Utils.showPanel('thankyou');
          }
        });
        return false;
      });

      if (Config.get('take-picture')) {

        $('#picture .skip').click(function() {
          Photobooth.teardown(!stream_always_on, function() {
            Utils.showPanel('thankyou');
            Utils.setActiveStep('#step_thankyou');
            // make sure there previous mug thumbnail is hidden
            $('#thankyou .thumbnail').hide();
          });
          return false;
        });

        $('a.snap').click(function(e) {
          e.preventDefault();

          var flash = $('.flash').show();
          setTimeout(function() {
            flash.addClass('fadeout');
            setTimeout(function() {
              flash.hide().removeClass('fadeout');
            }, 1000);
          }, 200);

          // Hide the photobooth before showing the preview
          var photoboothContainer = document.querySelector('#photobooth_container');
          photoboothContainer.style.display = "none";

          var canvas = Photobooth.getCanvas();
          document.getElementById('shutter-sound').play();
          canvas.toBlob(function(blob) {
            snap_blob = blob; // keep it in memory
          });
          $('.preview img').attr('src', canvas.toDataURL());
          $('#picture form').hide();
          $('.preview').show();
          Photobooth.teardown(!stream_always_on);

        });
      }

    },
    opened: function(id) {
      opened(id);
    }
  };
})();



var Location = (function() {
  var current_location_name, current_location_id;

  function clicked_location(event) {
    var $self = $(this);
    current_location_name = $self.data('name');
    localStorage.setItem('location-name', current_location_name);
    current_location_id = $self.data('id');
    localStorage.setItem('location-id', current_location_id);
    location_chosen();
    return false;
  }

  function location_chosen() {
    loader.hide();

    Config.set('current-location', current_location_id);
    $('footer .current-location a').text(current_location_name);

    Utils.showPanel('signin');
    Utils.setActiveStep('signin');
  }

  function location_not_chosen() {
    Utils.showPanel('location');

    var $choices = $('#location .available-locations');
    $('p', $choices).remove();
    $.getJSON(Config.get('locations-url'), function(response) {
      $.each(response.locations, function(i, each) {
        $('<a href="#">')
          .addClass('btn').addClass('btn-large')
          .text(each.name)
          .data('name', each.name)
          .data('id', each.id)
          .click(clicked_location)
          .appendTo($('<p>').appendTo($choices));
      });
    });
  }

  return {
     get_current_location: function() {
       return {id: current_location_id, name: current_location_name};
     },
     init: function() {
       $('footer .current-location a').click(function() {
         location_not_chosen();
         return false;
       });

       current_location_name = localStorage.getItem('location-name');
       current_location_id = localStorage.getItem('location-id');
       if (current_location_name && current_location_id) {
         location_chosen();
       } else {
         location_not_chosen();
       }

     }
  };
})();


// Find the right method, call on correct element
function launchFullScreen(element) {
  if (element.requestFullScreen) {
    element.requestFullScreen();
  } else if(element.mozRequestFullScreen) {
    element.mozRequestFullScreen();
  } else if(element.webkitRequestFullScreen) {
    element.webkitRequestFullScreen();
  }
}
document.addEventListener("fullscreenchange", function(e) {
  if (!$('a.fullscreen:visible').length) {
    $('a.fullscreen').show();
  }
});
document.addEventListener("mozfullscreenchange", function(e) {
  if (!$('a.fullscreen:visible').length) {
    $('a.fullscreen').show();
  }
});

$(function() {
    // Prevent the browser from jumping to the anchor
    window.addEventListener('hashchange', function(event) {
        window.scrollTo(0, 0);
    }, false);

  $('a.fullscreen').click(function(e) {
    e.preventDefault();
    // Launch fullscreen for browsers that support it!
    launchFullScreen(document.documentElement); // the whole page
    setTimeout(function() {
      $('a.fullscreen').hide();
    }, 2 * 1000);
  });

  loader = $('#loading');

  Location.init();
  SignIn.init();

  $(document).ajaxStart(function() {
    loader.show();
  });

  $(document).ajaxStop(function() {
    loader.hide();
  });

  $(document).ajaxError(function(event, jqxhr, settings, exception) {
    $('#loading').hide();
    Utils.ajax_error("Internal server error", jqxhr.responseText, function() {
      // reset_all() ??
    });
  });
});
