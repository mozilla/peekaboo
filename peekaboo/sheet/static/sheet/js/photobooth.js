var Photobooth = (function() {

  var video;
  var canvas;
  var context;
  var imageFilter;
  var stream;

  // Alias the vendor prefixed variants of getUserMedia so we can access them
  // via navigator.getUserMedia
  navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia || navigator.msGetUserMedia;

  // Alias the vendor prefixed variants of the URL object so that we can access them
  // via window.URL
  window.URL = window.URL || window.webkitURL || window.mozURL || window.msURL;

  // Alias the vendor prefixed variants of requestAnimationFrame so that we can access
  // them via window.requestAnimationFrame fallback to setTimeout at 60hz if not supported.
  window.requestAnimationFrame = (function() {
    return window.requestAnimationFrame  ||
      window.webkitRequestAnimationFrame ||
      window.mozRequestAnimationFrame    ||
      window.oRequestAnimationFrame      ||
      window.msRequestAnimationFrame     ||
      function (callback) {
        window.setTimeout(callback, 1000 / 60);
      };
  })();

  // This function will be called if a webcam is available and the user has
  // granted access for the web application to use it.
  function successCallback(_stream) {
    // store this in the "closure global" space so we can stop it later
    stream = _stream;

    // Firefox has a special property that you can use to associate the stream with the
    // video object.  Other browsers require you to use createObjectURL.
    if (video.mozSrcObject !== undefined) {
      video.mozSrcObject = stream;
    }
    else {
      video.src = (window.URL && window.URL.createObjectURL(stream)) || stream;
    }
    video.play();

    console.log("You should be seeing video from your camera.");

    // capture the first frame of video and start the animation loop that
    // continuously update the video to the screen
    update();
  }

  function failureCallback() {
    console.warn('Unable to start getUserMedia');
    console.error(arguments);
  }

  // with the delta value
  brightness = function(delta) {
    return function (pixels, args) {
      var d = pixels.data;
      for (var i = 0; i < d.length; i += 4) {
        d[i] += delta;     // red
        d[i + 1] += delta; // green
        d[i + 2] += delta; // blue
      }
      return pixels;
    };
  };

  function processImage() {
    if (canvas.width > 0 && canvas.height > 0) {
      if (imageFilter) {
        context.putImageData(imageFilter.apply(null,
         [context.getImageData(0, 0, canvas.width, canvas.height)]), 0, 0);
      }
    }
  }

  function processVideoFrame() {
    // We have to check for the video dimensions here.
    // Dimensions will be zero until they can be determined from
    // the stream.
    if (context && video.videoWidth > 0 && video.videoHeight > 0) {
      // Resize the canvas to match the current video dimensions
      if (canvas.width != video.videoWidth) {
        canvas.width = video.videoWidth;
      }
      if (canvas.height != video.videoHeight) {
        canvas.height = video.videoHeight;
      }

      // Copy the current video frame by drawing it onto the
      // canvas's context
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      processImage(canvas);
    }
  }

  var frameNumber = 0;
  var startTime = null;

  function update() {

    processVideoFrame();

    frameNumber++;
    // console.log(frameNumber);
    // console.log($('.debugging-fps'));
    if (startTime === null) {
      startTime = (new Date).getTime(); // in milliseconds
    }
    // Every 60 frames calculate our actual framerate and display it
    if (frameNumber >= 60) {
      var currentTime = (new Date).getTime();            // in milliseconds
      var deltaTime = (currentTime - startTime) / 1000.0;  // in seconds
      $('.debugging-fps').text(Math.floor(frameNumber/deltaTime) + " fps");
      startTime = currentTime;
      frameNumber = 0;
    }
    requestAnimationFrame(update);
  }

  function clearCanvas() {
    context.clearRect(0, 0, canvas.width, canvas.height);
  }

  return {
     setup: function(callback) {
       callback = callback || null;

       imageFilter = null;
       //setFilter(null);

       // Get the DOM object that matches the first video tag on the page
       video = document.querySelector('video');

       canvas = document.querySelector("canvas");
       context = canvas.getContext("2d");

       console.log("Waiting for you to grant access to the camera...");

       // We can retrieve the video dimensions from the video object once we have
       // registered for and received the loadeddata event
       video.addEventListener('loadeddata', function(e) {
         console.log('loadeddata Video dimensions: ' + video.videoWidth + ' x ' + video.videoHeight);
       }, false);

       video.addEventListener('playing', function(e) {
         console.log('play Video dimensions: ' + video.videoWidth + ' x ' + video.videoHeight);
       }, false);

       if (!navigator.getUserMedia) {
         throw 'The navigator.getUserMedia() method not supported in this browser.';
       }

       // Ask the user for access to the camera
       navigator.getUserMedia(
         {video: true},
         function(stream) {
           clearCanvas();
           successCallback(stream);
           if (callback) callback(true);
         }, failureCallback);
         if (callback) callback(false);
     },
     teardown: function(stopstream, callback) {
       if (stopstream) {
         stream.stop();
       }
       if (callback) callback();
     },
     getCanvas: function() {
       return canvas;
     },
     setFilter: function(f) {
       imageFilter = f;
     }
  };

})();
