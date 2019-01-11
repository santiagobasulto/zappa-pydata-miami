$('.main-chart-controls span').on('click', function(evt){
  var self = $(this);
  var spinner = $('.loading-spinner');
  var bokehContainer = $('#bokeh-container')
  if(self.hasClass('active')){
    return
  }
  bokehContainer.remove()
  bokehContainer = $('.bokeh-wrapper').append('<div id="bokeh-container"></div>')
  spinner.show();
  var symbol = $(this).data('symbol');
  var url = window.API_ENDPOINTS[symbol]
  fetch(url)
    .then(function(response) { return response.json(); })
    .then(function(item) {
      $('.main-chart-controls span.active').removeClass('active');
      self.addClass('active')
      spinner.hide();
      Bokeh.embed.embed_item(item, "bokeh-container");
    })
})

$('*[data-symbol="btcusd"]').click()
