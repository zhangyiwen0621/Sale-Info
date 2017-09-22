function populateList() {
    $.get("/SaleInfo/get_favorite_info")
      .done(function(data) {
          var list = $("#list");
          list.html('');
          for (var i = 0; i < data.sale_infos.length; i++) {
            var sale_info = data.sale_infos[i];
            var new_sale_info = $(sale_info.html);

            list.prepend(new_sale_info);
          }
      });
}

function getUpdates() {
    $.get("/SaleInfo/get_favorite_info")
      .done(function(data) {
        var list = $("#list");
        list.html('');
        for (var i = 0; i < data.sale_infos.length; i++) {
          var sale_info = data.sale_infos[i];
          var new_sale_info = $(sale_info.html);

          list.prepend(new_sale_info);
        }
      });
}


$(document).ready(function () {
  populateList();

  window.setInterval(getUpdates, 57000);

  // CSRF set-up copied from Django docs
  function getCookie(name) {  
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});

