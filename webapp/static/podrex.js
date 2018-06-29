// partially from Matt Drury - https://github.com/madrury/madrury.github.io/blob/master/smoothers/js/parameter-ui.js
get_favorites = function() {
    let fave_parameters = {};
    let favorites = document.getElementsByClassName("chosen-select-deselect");
    for (let favorite of favorites) {
        fave_parameters[$(favorite).val()] = 5;
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
submit = function() {
    fave_parameters = get_favorites()
    thumbs = get_thumbs()
    $.post({
        url: "/predictions/",
        contentType: "application/json",
        data: JSON.stringify({
            "favorites": fave_parameters,
            "thumbs": thumbs
        }),
        success: function(result) {
            {
                window.location.href = '/recommendations/' + result;
            };
        }
    });
}

thumbs_listener = function() {
    $('.thumbs').on('click', function() {
        let id = $(this).attr('id');
        let pid = $("#" + id).attr('data-s-id');
        let t_type = $("#" + id).attr('data-t-type');
        let active = $("#" + id).attr('aria-pressed');
        if (active === "false") {
            if (t_type === "up") {
                let other = "#down-" + pid
                setTimeout(function() {
                    $(other).removeClass('active').attr('aria-pressed', false);
                }.bind(this), 10);
            } else {
                let other = "#up-" + pid
                setTimeout(function() {
                    $(other).removeClass('active').attr('aria-pressed', false);
                }.bind(this), 10);
            }
        } else {}
    });
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
                            .attr("src", "http://podcasts-dragon-nba-who.s3-website-us-west-2.amazonaws.com/static/artwork/" + result["podcast_art_id"] + ".jpg")
                            .attr("style", "margin-top:1rem;")
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
        //console.log(update_flag)
        for (let select_menu of curr_selects) {
            //console.log($(select_menu).val())
            if ($(select_menu).val() === "") {
                update_flag = false
            } else {}
        }
        //console.log(update_flag)
        if (update_flag === true) {
            new_favorite_podcast()
        } else {}
    });
};

$(".chosen-select-deselect").chosen().change(function() {
    var id = $(this).attr('id');
    //console.log(id);
});
var div_counter = 0;
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
                        .text("Another of my favorite podcasts:")
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
    //console.log(curr_div_id)
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
                if (card["itunes_url"] !== null) {
                    itunes_string = $("<a/>")
                        .attr("href", card["itunes_url"])
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-image")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/itunes-square.png")
                        )
                }
                if (card["stitcher_url"] !== null) {
                    stitcher_string = $("<a/>")
                        .attr("href", card["stitcher_url"])
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-image")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/stitcher-square.png")
                        )
                }
                if (card["podcast_url"] !== null) {
                    web_url = $("<a/>")
                        .attr("href", card["podcast_url"])
                        .append(
                            $("<img/>")
                            .attr("class","podcast-link link-icon")
                            .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/white-link.png")
                        )
                }
                $("#"+result_type).append(
                    $("<div/>")
                    .attr("class", "card-col col-lg-2 col-md-4 col-sm-6 portfolio-item")
                    .attr("id", "recommendation"+card["sid"])
                    .append(
                          $("<div/>")
                          .attr("class", "card-con card")
                          .append(
                              $("<a/>")
                              .attr("href", "#")
                                 .append(
                                     $("<img/>")
                                      .attr("src", "http://podcasts-dragon-nba-who.s3-website-us-west-2.amazonaws.com/static/artwork/"+card["art_id"]+".jpg")
                                      .addClass("card-img-top")
                                      )
                           )
                          .append(
                             $("<div/>")
                               .addClass("card-body")
                               .append(
                                 $("<h4/>")
                                   .addClass("card-title text-center thumb-card")
                                   .append(
                                       $("<a/>")
                                       .text(card["title"])
                                   )
                               )
                               .append(
                                   $("<button/>")
                                   .attr("id", "up-"+card["sid"])
                                   .attr("data-s-id", card["sid"])
                                   .attr("data-t-type", "up")
                                   .attr("class", "btn btn-light thumbs thumbs-up")
                                   .attr("type", "button")
                                   .attr("data-toggle", "button")
                                   .attr("aria-pressed", "false")
                                   .attr("autocomplete", "off")
                                   .append(
                                       $("<img/>")
                                       .attr("class", "thumb-img")
                                       .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/thumbs-up-small.png")
                                   )
                               )
                               .append(
                                   $("<button/>")
                                   .attr("id", "down-"+card["sid"])
                                   .attr("data-s-id", card["sid"])
                                   .attr("data-t-type", "down")
                                   .attr("class", "btn btn-light thumbs thumbs-down")
                                   .attr("type", "button")
                                   .attr("aria-pressed", "false")
                                   .attr("autocomplete", "off")
                                   .append(
                                       $("<img/>")
                                       .attr("class", "thumb-img")
                                       .attr("src", "../static/x.png")
                                   )
                               )
                               .append(
                                   $("<button/>")
                                   .attr("class", "desc-btn btn btn-outline-secondary btn-block")
                                   .attr("data-toggle", "modal")
                                   .attr("data-target", "#modal"+card["sid"])
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
                   )
                   }
                   $(".thumbs-down").on("click", destroy_card)
               };

destroy_card = function(){
    $(this).closest(".card-col").remove()
};
chosen_listener()
thumbs_listener()
