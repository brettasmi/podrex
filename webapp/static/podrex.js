get_favorites = function() {
    let fave_parameters = {};
    let favorites = document.getElementsByClassName("chosen-select-deselect");
    for (let favorite of favorites) {
        if ($(favorite).val() !== "") {
            fave_parameters[$(favorite).val()] = 5;
        }
    }
    return fave_parameters;
};

get_thumbs = function() {
    let results = {};
    let buttons = $(".active.thumbs")
    for (let button of buttons) {
        if ($(button).attr("data-t-type") === "up") {
            results[$(button).attr("data-s-id")] = 5;
        } else {
            results[$(button).attr("data-s-id")] = 1;
        }
    }
    return results;
};
get_search_sids = function() {
    let search_cards = $(".card-body")
    let search_sids = []
    for (let curr_card of search_cards) {
        search_sids.push($(curr_card).attr("data-s-id"))
    }
    return search_sids
};
submit = function() {
    fave_parameters = get_favorites()
    thumbs = get_thumbs()
    $.post({
        url: "/predictions/",
        contentType: "application/json",
        data: JSON.stringify({
            "favorites": fave_parameters,
            "thumbs": thumbs,
            "dismissed": dismissed
        }),
        success: function(result) {
            if (result === "empty"){
                $("#recommendations").fadeOut(750, function() { $(this).remove(); });
            } else {
                if (!$("#recommendations").length ){
                    $("#main-content").append(
                        $("<div/>")
                        .attr("id", "recommendations")
                        .attr("class", "card-deck")
                    )
                } else {
                }
                $(".thumbs-up").not(".active").closest(".card-col").fadeOut(750, function(){$(this).remove(); });
                populate_cards(result, "recommendations")
                create_save_button()
            };
        }
    });
}

create_save_button = function() {
    if (!$("#save-button").length ) {
        $("<button/>")
            .attr("id","save-button")
            .attr("class", "btn btn-primary add-podcast-button")
            .text("Save and Visualize")
            .hide()
            .appendTo("#welcome-text")
            .fadeIn(1000)

        $("#save-button").on("click", save_recommendations)
    }
}

save_recommendations = function(result) {
    let likes = []
    let search_results = []
    if ($("#search-results").length ) {
        console.log("hello")
        search_results = search_results.concat(get_search_sids())
        console.log(search_results)
    } else {
        likes = likes.concat(Object.keys(get_favorites()), Object.keys(get_thumbs()))
    }
    let go_url = "/recommendations/?"
    for (let like of likes) {
        go_url += ("like=" + like + "&")
    }
    for (let dnr of dismissed) {
        go_url += ("dismissed=" + dnr + "&")
    }
    for (let search_result of search_results) {
        go_url += ("card="+ search_result + "&")
    }
    window.location.href = go_url
};
thumbs_listener = function() {
    let id = $(this).attr('id'); // div id
    let pid = $("#" + id).attr('data-s-id'); // data id
    let t_type = $("#" + id).attr('data-t-type'); // thumb type (up/down)
    let active = $("#" + id).attr('aria-pressed');
    if (active === "false") {
        if (t_type === "up") {
            let other = "#down-" + pid
                $(other).removeClass('active').attr('aria-pressed', false);
        } else {
            let other = "#up-" + pid
                $(other).removeClass('active').attr('aria-pressed', false);
        }
    }
    setTimeout(submit, 100)
}

chosen_listener = function() {
    $(".chosen-select-deselect").chosen().change(function() {
        let id = $(this).attr('id');
        var pid = $("#" + id).val();
        $.post({
            url: "/dd-update/",
            contentType: "application/json",
            data: JSON.stringify({
                "podcast": pid
            }),
            success: function(result) {
                $("#" + id + "-updated").empty()
                if (result["action"] === "populate") {
                    $("#" + id + "-updated").append(
                        $("<a/>")
                        .attr("href", "#")
                        .append(
                            $("<img/>")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/artwork/" + result["podcast_art_id"] + ".jpg")
                            .attr("style", "margin-top:1rem;width:60%;height:60%;margin-left:20%;margin-right:20%;")
                            .addClass("card-img-top")
                        )
                    );
                    $("#" + id + "-updated").append(
                        $("<div/>")
                        .append(
                            $("<button/>")
                            .attr("type", "button")
                            .attr("class", "btn btn-outline-secondary btn-block")
                            .attr("style", "margin-top:1rem;")
                            .attr("data-toggle", "modal")
                            .attr("data-target", "#modal" + pid)
                            .text("See Description")
                        )
                        .append(
                            $("<div/>")
                            .attr("class", "modal fade")
                            .attr("id", "modal" + pid)
                            .attr("tabindex", "-1")
                            .attr("role", "dialog")
                            .attr("aria-labelledby", "exampleModalLabel")
                            .attr("aria-hidden", "true")
                            .append(
                                $("<div/>")
                                .attr("class", "modal-dialog")
                                .attr("role", "document")
                                .append(
                                    $("<div/>")
                                    .attr("class", "modal-content")
                                    .append(
                                        $("<div/>")
                                        .attr("class", "modal-header")
                                        .append(
                                            $("<h5/>")
                                            .attr("class", "modal-title")
                                            .attr("id", "modal-" + pid + "-content")
                                            .text(result["podcast_name"])
                                        )
                                        .append(
                                            $("<button/>")
                                            .attr("type", "button")
                                            .attr("class", "close")
                                            .attr("data-dismiss", "modal")
                                            .attr("aria-label", "Close")
                                            .append(
                                                $("<span/>")
                                                .attr("aria-hidden", "true")
                                                .text("x")
                                            )
                                        )
                                    )
                                    .append(
                                        $("<div/>")
                                        .attr("class", "modal-body")
                                        .append(
                                            $("<p/>")
                                            .attr("class", "card-text")
                                            .text(result["podcast_description"])
                                        )
                                    )
                                    .append(
                                        $("<div/>")
                                        .attr("class", "modal-footer")
                                        .append(
                                            $("<button/>")
                                            .attr("type", "button")
                                            .attr("class", "btn btn-secondary")
                                            .attr("data-dismiss", "modal")
                                            .text("Close")
                                        )
                                    )
                                )
                            )
                        )
                    );
                } else {}
            }
        });
        let curr_selects = $(".chosen-select-deselect")
        let update_flag = true
        for (let select_menu of curr_selects) {
            if ($(select_menu).val() === "") {
                update_flag = false
            } else {}
        }
        if (update_flag === true) {
            new_favorite_podcast()
        } else {}
        setTimeout(submit, 100)
    });
};

chosen_change = function() {$(".chosen-select-deselect").chosen().change(function() {
    var id = $(this).attr('id');
});};

new_favorite_podcast = function() {
    div_counter++
    let curr_div_id = "fave" + div_counter
    $("#favorites-row").append(
        $("<div/>")
        .addClass("col-lg-3 col-md-4 col-sm-6 portfolio-item")
        .append(
            $("<div/>")
            .addClass("card h-100")
            .append(
                $("<a/>")
                .attr("href", "#")
            )
            .append(
                $("<div/>")
                .addClass("card-body")
                .append(
                    $("<h5/>")
                    .addClass("card-title text-center")
                    .append(
                        $("<a/>")
                        .text("Another favorite podcast")
                    )
                )
                .append(
                    $("<div/>")
                    .append(
                        $("<select/>")
                        .attr("id", curr_div_id)
                        .attr("data-placeholder", "Choose a podcast..")
                        .attr("tabindex", "2")
                        .attr("style", "width:100%;")
                        .addClass("chosen-select-deselect")
                        .append(
                            $("<option/>")
                            .attr("value", "")
                        )
                    )
                )
                .append(
                    $("<div/>")
                    .attr("id", curr_div_id + "-updated")
                )
            )
        )
    )
    $("#" + curr_div_id).chosen({
        allow_single_deselect: true,
        no_results_text: "No podcasts matching that search. More podcasts coming soon."
    });
    populate_dropdown(curr_div_id)
    chosen_listener()
}

populate_dropdown = function(id) {
    $.getJSON("../static/data/podcast_pid_list.json", function(data) {
        $.each(data, function(key, value) {
            $("#" + id).append($("<option />").val(value[0]).text(value[1]));
        });
        $("#" + id).trigger("chosen:updated");
    });
}

populate_cards = function(card_list, result_type){
            for (let card of card_list) {
                let id = card["sid"]
                let itunes_string = ""
                let stitcher_string = ""
                let web_url = ""
                let thumbs_up = ""
                let dismiss_button = ""
                if (card["itunes_url"] !== null) {
                    itunes_string = $("<a/>")
                        .attr("href", card["itunes_url"])
                        .attr("title", card["title"] + " at iTunes")
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-image")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/itunes-square.png")
                        )
                }
                if (card["stitcher_url"] !== null) {
                    stitcher_string = $("<a/>")
                        .attr("href", card["stitcher_url"])
                        .attr("title", card["title"] + " at Stitcher")
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-image")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/stitcher-square.png")
                        )
                }
                if (card["podcast_url"] !== null) {
                    web_url = $("<a/>")
                        .attr("href", card["podcast_url"])
                        .attr("title", card["title"] + " website")
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-icon")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/white-link.png")
                        )
                }
                if (result_type === "recommendations") {
                    thumbs_up = $("<button/>")
                        .attr("id", "up-"+card["sid"])
                        .attr("data-s-id", card["sid"])
                        .attr("data-t-type", "up")
                        .attr("class", "btn btn-light thumbs thumbs-up")
                        .attr("type", "button")
                        .attr("data-toggle", "button")
                        .attr("aria-pressed", "false")
                        .attr("autocomplete", "off")
                        .attr("title", "I know and like this podcast.")
                        .append(
                            $("<img/>")
                            .attr("class", "thumb-img")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/thumbs-up-small.png")
                        )
                    dismiss_button = $("<button/>")
                        .attr("id", "down-"+card["sid"])
                        .attr("data-s-id", card["sid"])
                        .attr("data-t-type", "down")
                        .attr("class", "btn btn-light thumbs thumbs-down")
                        .attr("type", "button")
                        .attr("aria-pressed", "false")
                        .attr("autocomplete", "off")
                        .attr("title", "Permanently remove from your recommendations.")
                        .append(
                            $("<img/>")
                            .attr("class", "thumb-img")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/x.png")
                        )
                }
                let new_card = $("<div/>")
                    new_card.attr("class", "card-col col-lg-2 col-md-4 col-sm-6 portfolio-item")
                    .attr("id", "recommendation"+card["sid"])
                    .append(
                          $("<div/>")
                          .attr("class", "card-con card")
                          .append(
                              $("<a/>")
                              .attr("href", "#")
                                 .append(
                                     $("<img/>")
                                      .attr("src", "	https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/artwork/"+card["art_id"]+".jpg")
                                      .addClass("card-img-top")
                                      )
                           )
                          .append(
                             $("<div/>")
                               .addClass("card-body")
                               .attr("data-s-id", card["sid"])
                               .append(
                                 $("<h5/>")
                                   .addClass("card-title text-center thumb-card")
                                   .append(
                                       $("<a/>")
                                       .text(card["title"])
                                   )
                               )
                               .append(thumbs_up)
                               .append(dismiss_button)
                               .append(
                                   $("<button/>")
                                   .attr("class", "desc-btn btn btn-outline-secondary btn-block")
                                   .attr("data-toggle", "modal")
                                   .attr("data-target", "#modal"+card["sid"])
                                   .attr("title", "View podcast description.")
                                   .text("Description")
                               )
                               .append(
                                   $("<div/>")
                                   .attr("class", "modal fade")
                                   .attr("id", "modal"+card["sid"])
                                   .attr("tabindex", "-1")
                                   .attr("role", "dialog")
                                   .attr("aria-hidden", "true")
                                   .append(
                                       $("<div/>")
                                       .attr("class", "modal-dialog")
                                       .attr("role", "document")
                                       .append(
                                           $("<div/>").attr("class", "modal-content")
                                           .append(
                                               $("<div/>").attr("class", "modal-header")
                                               .append(
                                                   $("<h5/>")
                                                   .attr("class", "modal-title")
                                                   .attr("id", "modal"+card["sid"]+"-content")
                                                   .text(card["title"])
                                               )
                                               .append(
                                                   $("<button/>")
                                                   .attr("class", "close")
                                                   .attr("data-dismiss", "modal")
                                                   .attr("aria-label", "Close")
                                                   .attr("title", "Close description box")
                                                   .append(
                                                       $("<span/>").attr("aria-hidden", "true").html("&times;")
                                                   )
                                               )
                                           )
                                           .append(
                                               $("<div/>").attr("class", "modal-body")
                                               .append($("<p/>").attr("class", "card-text").text(card["description"]))
                                           )
                                           .append(
                                               $("<div/>")
                                               .attr("class", "modal-footer")
                                               .append(
                                                   $("<button/>")
                                                   .attr("class", "btn btn-secondary")
                                                   .attr("data-dismiss", "modal")
                                                   .text("Close")
                                               )
                                           )
                                       )
                                   )
                               )
                               .append(
                                   $("<div/>")
                                   .attr("class", "links-box")
                                   .append(itunes_string)
                                   .append(stitcher_string)
                                   .append(web_url)
                               )
                          )
                       )
                   $(new_card).hide().appendTo("#"+result_type).fadeIn(1000)
                   }
                   $(".thumbs-down").on("click", destroy_card)
                   $(".thumbs-up").on("click", thumbs_listener)
               };

destroy_card = function(){
    dismissed.push($(this).attr("data-s-id"))
    $(this).closest(".card-col").fadeOut(500, function() { $(this).remove(); });
};

search_box = function() {
    $("#search-button").before(
        $("<input/>")
            .attr("id", "text-search")
            .attr("class", "add-podcast-button")
            .attr("style","width:95%;")
            .attr("placeholder", "ex. data science")
    )
    .attr("data-clicked","true")
    .text("Search");

    $('#text-search').keypress(function(e){
        if(e.which == 13){//Enter key pressed
            $('#search-button').click();//Trigger search button click event
        }
    });
}

$("#search-button").on("click", function (){
    if ($(this).attr("data-clicked") === "false") {
        search_box()
    } else {
        submit_text_search($("#text-search").val())
    }
});

submit_text_search = function(text){
    $(".card").fadeOut(500, function() { $(this).remove(); })
    $.post({
        url: "/text-search/",
        contentType: "application/json",
        data: JSON.stringify({"search":text}),
        success: function(result){
            if (!$("#search-results").length ){
                $("#main-content").append(
                    $("<div/>")
                    .attr("id", "search-results")
                    .attr("class", "card-deck")
                )
            } else {
                $("#search-results").fadeOut(300, function() { $(this).empty(); });
            }
            setTimeout(function () { populate_cards(result, "search-results"); }, 350)
            $("#search-results").fadeIn(350);
            create_save_button()
        }
    });
};
let dismissed = []
$(chosen_listener())

// Chosen touch support via https://realize.be/blog/mobile-support-chosen
if ($('.chosen-container').length > 0) {
  $('.chosen-container').on('touchstart', function(e){
    e.stopPropagation(); e.preventDefault();
    // Trigger the mousedown event.
    $(this).trigger('mousedown');
  });
}
