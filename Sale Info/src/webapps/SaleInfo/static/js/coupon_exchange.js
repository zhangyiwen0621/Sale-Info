function populateList() {
    console.log('populateList');
    $.get("/SaleInfo/coupon_exchange/check_expired").done(function() {
        console.log('check expiration done.')
        $.get("/SaleInfo/coupon_exchange/get_coupons_owned").done(function(data) {
            console.log('get_coupons_owned done.')
            console.log(data['max-time'])
            var owned_coupon_list = $("#owned-coupon-list");
            var exchange_coupon_list = $("#exchange-coupon-select")
            var match_coupon_list = $("#match-coupon-list")

            owned_coupon_list.data('max-time', data['max-time']);
            owned_coupon_list.html('')
            exchange_coupon_list.html('')
            match_coupon_list.html('')

            console.log("exchange coupons #: " + data.coupons.length)
            console.log("match coupons #: " + data.match_coupons.length)

            // Populate the Owned_coupon and exchange_select
            for (var i = 0; i < data.coupons.length; i++) {
                coupon = data.coupons[i];
                var new_coupon = $(coupon.owned_html);
                new_coupon.data("coupon-id", coupon.id);
                
                if (!coupon.rated) {
                    new_couponDIV = new_coupon.find("div");
                    new_couponDIV.append("<hr><form id='rate_form_"+coupon.id+"' method='POST'><select class='form-control' style='width:100px; display:inline-block;' id='rate' name='rate'><option value='1'>1</option><option value='2'>2</option><option value='3'>3</option><option value='4'>4</option><option value='5'>5</option></select>&nbsp<button class='btn btn-warning btn-lg' id='rate-coupon-btn'>Rate This Coupon!</button></form>");
                }
                else {
                    new_couponDIV = new_coupon.find("div");
                    new_couponDIV.append("<br><button class='btn btn-warning btn-lg' id='rated-coupon-btn'>You've Rated This Coupon!</button>");
                }
                new_coupon.find("#delete-coupon-btn").click(coupon, deleteCoupon);
                new_coupon.find("#rate-coupon-btn").click(coupon, rateCoupon);
                owned_coupon_list.prepend(new_coupon);

                exchange_coupon_list.data('max-time', data['max-time']);
                if(!coupon.in_exchange) {
                    exchange_coupon_list.data('max-time', data['max-time']);
                    var new_coupon_exchange = $(coupon.exchange_html);
                    new_coupon_exchange.data("coupon-id", coupon.id);
                    exchange_coupon_list.prepend(new_coupon_exchange);
                }
            }

            // Populate the match_list
            for (var i = 0; i < data.match_coupons.length; i++) {
                match_coupon = data.match_coupons[i];
                var new_match_coupon = $(match_coupon.match_html);
                new_match_coupon.data("coupon-id", match_coupon.id);
                match_coupon_list.prepend(new_match_coupon);
                
                // append match_own_coupon
                match_own_coupon = data.match_own_coupons[i];
                new_match_own_coupon = $(match_own_coupon.match_own_html);
                new_match_own_coupon.data("coupon-id", match_own_coupon.id);
                $("#match_" + match_coupon.id).find('#match_own_coupon').append(new_match_own_coupon);
                if (!data.exchanges[i]) {
                    new_match_couponDIV = $("#match_"+match_coupon.id).find("div#match_html");
                    new_match_couponDIV.append("<hr><button class='btn btn-lg btn-success' id='match-btn'>Exchange this coupon!</button>");
                }
                else {
                    new_match_couponDIV = $("#match_"+match_coupon.id).find("div#match_html");
                    new_match_couponDIV.append("<hr><button class='btn btn-lg btn-warning' id='pending-match-btn'>Pending for Exchange...</button>");
                }
                new_match_coupon.find("#match-btn").click({match_coupon:match_coupon, match_own_coupon:match_own_coupon}, finishExchange);
            }
        });
    });
}

function addCoupon() {
    console.log("addCoupon")
    var coupon_form = $('#add-coupon-form');
    var exchange_form = $('#coupon-exchange-list');
    coupon_form.unbind('submit').submit(function(evt) {
        evt.preventDefault();

        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data:formData,
            cache:false,
            contentType: false,
            processData: false,
            success: function(data) {
                getUpdatedCoupon();
                coupon_form.trigger("reset");
                exchange_form.trigger("reset");
                $.notify({
                    message:"You just put new coupon in your pocket:)"
                },{
                    type:'success'
                });
            },
            error: function(data) {
                alert(data);
            }
        });
    });
}

function deleteCoupon(e) {
    console.log(e.data.id);
    $.post("/SaleInfo/coupon_exchange/delete_coupon/" + e.data.id)
      .done(function(data) {
          getUpdatedCoupon();
          $.notify({
                message:"You delete a coupon from your pocket."
            },{
                type:'danger'
            });
      });
}

function getUpdatedCoupon() {
    var owned_coupon_list = $("#owned-coupon-list");
    var exchange_coupon_list = $("#exchange-coupon-select");
    var match_coupon_list = $("#match-coupon-list");
    var max_time = owned_coupon_list.data("max-time");
    console.log('Updating coupons...');
    console.log(max_time);

    $.get("/SaleInfo/coupon_exchange/check_expired").done(function() {
        $.get("/SaleInfo/coupon_exchange/get_changes_owned/"+max_time)
          .done(function(data) {
            console.log('get_changes_owned done');
            owned_coupon_list.data('max-time', data['max-time']);
            // Update the own_coupon_list and exchange_coupon_select
            for (var i = 0; i < data.coupons.length; i++) {
                var coupon = data.coupons[i];
                if (!coupon.valid) {
                    $("#coupon_" + coupon.id).remove();
                    $("#" + coupon.id).remove();
                }
                else if (coupon.profile_id != data.profile_id) {
                    $("#coupon_" + coupon.id).remove();
                    $("#" + coupon.id).remove();
                }
                else {
                    $("#coupon_" + coupon.id).remove();
                    var new_coupon = $(coupon.owned_html);
                    new_coupon.data("coupon-id", coupon.id);
                    if (!coupon.rated) {
                        new_couponDIV = new_coupon.find("div");
                        new_couponDIV.append("<hr><form id='rate_form_"+coupon.id+"' method='POST'><select class='form-control' style='width:100px; display:inline-block;' id='rate' name='rate'><option value='1'>1</option><option value='2'>2</option><option value='3'>3</option><option value='4'>4</option><option value='5'>5</option></select>&nbsp&nbsp<button class='btn btn-warning btn-lg' id='rate-coupon-btn'>Rate This Coupon!</button></form>");
                    }
                    else {
                        new_couponDIV = new_coupon.find("div");
                        new_couponDIV.append("<br><button class='btn btn-warning btn-lg' id='rated-coupon-btn'>You've Rated This Coupon!</button>");
                    }
                    new_coupon.find("#delete-coupon-btn").click(coupon, deleteCoupon);
                    new_coupon.find("#rate-coupon-btn").click(coupon, rateCoupon);
                    owned_coupon_list.prepend(new_coupon);

                    exchange_coupon_list.data('max-time', data['max-time']);
                    if (!coupon.in_exchange && !coupon.rated) {
                        var new_coupon_exchange = $(coupon.exchange_html);
                        new_coupon_exchange.data("coupon-id", coupon.id);
                        exchange_coupon_list.prepend(new_coupon_exchange);
                        $.notify({
                            message:"You have new coupons."
                        },{
                            type:'info'
                        });
                    }
                    else if (coupon.in_exchange) {
                        $("#" + coupon.id).remove();
                    }
                }
            }

            match_coupon_list.html('')
            console.log("match_coupons #: " + data.match_coupons.length);
            // Update the match_list
            for (var i = 0; i < data.match_coupons.length; i++) {
                match_coupon = data.match_coupons[i];
                var new_match_coupon = $(match_coupon.match_html);
                new_match_coupon.data("coupon-id", match_coupon.id);
                match_coupon_list.prepend(new_match_coupon);
                
                // append match_own_coupon
                match_own_coupon = data.match_own_coupons[i];
                new_match_own_coupon = $(match_own_coupon.match_own_html);
                new_match_own_coupon.data("coupon-id", match_own_coupon.id);
                $("#match_" + match_coupon.id).find('#match_own_coupon').append(new_match_own_coupon);

                // console.log(data.exchanges[i])
                if (!data.exchanges[i]) {
                    new_match_couponDIV = $("#match_"+match_coupon.id).find("div#match_html");
                    new_match_couponDIV.append("<hr><button class='btn btn-lg btn-success' id='match-btn'>Exchange this coupon!</button>");
                }
                else {
                    new_match_couponDIV = $("#match_"+match_coupon.id).find("div#match_html");
                    new_match_couponDIV.append("<hr><button class='btn btn-lg btn-warning' id='pending-match-btn'>Pending for Exchange...</button>");
                }
                new_match_coupon.find("#match-btn").click({match_coupon:match_coupon, match_own_coupon:match_own_coupon}, finishExchange);
            }
          });
    });
}

function addExchange() {
    console.log("Add Coupon To Exchange System");
    var exchange_form = $('#coupon-exchange-list');
    var coupon_form = $('#add-coupon-form');
    exchange_form.unbind('submit').submit(function(evt) {
        evt.preventDefault();
        var formData = new FormData(this);
        var coupon_id = $('#exchange-coupon-select').children(":selected").attr("id");

        console.log(formData)
        console.log(coupon_id)
        // exchange_form.trigger("reset");
        $.ajax({
            type: 'POST',
            url: "/SaleInfo/coupon_exchange/add_exchange_coupon/"+coupon_id,
            data: formData,
            cache:false,
            contentType: false,
            processData: false,
            success: function(data) {
                getUpdatedCoupon();
                exchange_form.trigger("reset");
                coupon_form.trigger("reset");
            },
            error: function(xhr, status, error) {
                alert(xhr.responseText);
            }
        });
    });
}

function finishExchange(e) {
    console.log("Finish Exchange Process.")
    console.log("Match Coupon #: "+e.data.match_coupon.id)
    console.log("Match Own Coupon #: "+e.data.match_own_coupon.id)
    $.post("/SaleInfo/coupon_exchange/finish_exchange_coupon/" + e.data.match_coupon.id + "/" + e.data.match_own_coupon.id)
      .done(function(data) {
          getUpdatedCoupon();
          if (data) {
            $.notify({
                message:"You just exchange your coupon with others."
            },{
                type:'success'
            });
          }
      });
}

function rateCoupon(e) {
    console.log(e.data.id);
    var rate_form = $('#rate_form_'+e.data.id);
    var rate_id = '#rate_'+e.data.id
    console.log($('#rate option:selected').val())
    e.preventDefault();
    $.post("/SaleInfo/coupon_exchange/rate_coupon/"+e.data.id, {rate:$('#rate option:selected').val()}).done(function(data) {
        getUpdatedCoupon();
        console.log('success rate');
        
    });
    
}

$(document).ready(function () {
    // TODO: add handler for the post button
    $("#add-coupon-btn").click(addCoupon);
    $("#add-exchange-btn").click(addExchange);

    $("#datetimepicker").datetimepicker({
        format:'YYYY-MM-DD HH:mm:ss',
    });
    populateList();

    window.setInterval(populateList, 5000);

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