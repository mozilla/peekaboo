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
     general_error: function(msg, reload_tip) {
       console.log('XXX -- this needs a lot more work');
       alert(msg);
     }
  };
})();


var SignIn = (function() {
  var current_file;

  function submit(form) {
    var $form = $(form);
    $.ajax({
       url: $form.attr('action'),
      type: 'POST',
      dataType: 'json',
      data: $form.serializeObject(),
      success: function(response) {
        if (response.errors) {
          $.each(response.errors, function(key, errors) {
            if (key === '__all__') {
              Utils.general_error(errors.join('<br>'));
            } else {
              //console.log($('[name="' + key + '"]', form).parents('.control-group'));
              var $input = $('[name="' + key + '"]', form);
              $input
                .parents('.control-group')
                  .addClass('error');
              $input.on('change', function() {
                console.log('fixed');
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
          form.reset();
          $('#signin').hide();
          $('#picture .name').text(response.name);
          $('#picture').data('id', response.id);
          $('#picture').show(300);
        }
      },
      error: function(xhr, status, error_thrown) {
        var msg = status;
        if (xhr.responseText)
          msg += ': ' + xhr.responseText;
        Utils.general_error(msg, "Try again in a minute. Sorry.");
      }
    });
  }

  function upload_current_file(file, callback) {
    var fd = new FormData();
    fd.append('picture', file);
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

  function picture_changed(event) {
         var preview_img = $('#picture .preview img');
         var files = event.target.files;

         if (files && files.length > 0) {
           current_file = files[0];

           try {
             // Get window.URL object
             var URL = window.URL || window.webkitURL;


             // Create ObjectURL
             var imgURL = URL.createObjectURL(current_file);

             // Set img src to ObjectURL
             preview_img.attr('src', imgURL);
             console.log('imgURL', imgURL);

             // Revoke ObjectURL
             URL.revokeObjectURL(imgURL);
             $('#picture .preview').show();
           } catch (e) {
             try {
               // Fallback if createObjectURL is not supported
               var fileReader = new FileReader();
               fileReader.onload = function (event) {
                 //showPicture.src = event.target.result;
                 preview_img.attr('src', event.target.result);
                 console.log('event.target.result', event.target.result);

               };
               fileReader.readAsDataURL(current_file);
               $('#picture .preview').show();
             } catch (e) {
               // Display error message
               $('#picture .error span')
                 .text("Neither createObjectURL or FileReader are supported");
               $('#picture .error').show();
             }
           }
         }
  }

  return {
     init: function() {
       $('#signin form').submit(function() {
         submit(this);
         return false;
       });

       $('#picture input[type="file"]').change(picture_changed);
       $('#picture .proceed').click(function() {
         $('#picture .uploading').show();
         upload_current_file(current_file, function() {
           $('#picture .uploading').hide();
           $('#picture').hide();
           $('#thankyou').show(300);
         });
       });
     }
  }
})();

$(function() {
  SignIn.init();
});
