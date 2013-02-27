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

  return {
     init: function() {
       /* doesn't work
       $('.error input').on('change', function() {
         console.log('changed!');
         $(this).parent('div.error').removeClass('error');
       });
        */
       $('#signin form').submit(function() {
         submit(this);
         return false;
       });
     }
  }
})();

$(function() {
  SignIn.init();
});
