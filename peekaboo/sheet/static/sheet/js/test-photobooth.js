$(function() {
  Photobooth.setup(function() {
    $('.photobooth').show();
    console.log('Photobooth has been set up');
    var canvas = Photobooth.getCanvas();
    // $('.preview').show();
    $('a.snap').on('click', function(e) {
      e.preventDefault();
      var flash = $('.flash').show();
      setTimeout(function() {
        flash.addClass('fadeout');
        setTimeout(function() {
          flash.hide().removeClass('fadeout');
        }, 1000);
      }, 200);
      document.getElementById('shutter-sound').play();
      $('<img>')
        .attr('src', canvas.toDataURL())
        .css('width', 100)
        .appendTo($('#previews'));

    });
  });
});
