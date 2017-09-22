function changeStatus(e){
    var button = $(e.target);
    if (button.is("button")) {
      brand_id = button.val();
      if (button.text() == "Follow") {
        $.post("/SaleInfo/follow/" + brand_id)
          .done(function(data) {
            button.text("Unfollow");
            button.removeClass("btn-primary");
            button.addClass("btn-danger");
          });
      } else if (button.text() == "Unfollow") {
        $.post("/SaleInfo/unfollow/" + brand_id)
          .done(function(data) {
            button.text("Follow");
            button.removeClass("btn-danger");
            button.addClass("btn-primary");
          });
      }
    }
}

$(document).ready(function () {

  $("#brand-block").click(changeStatus);

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

