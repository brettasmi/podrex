submit = function(){
    let search = $("#text-search").val()
    $.post({
        url: "../text-search/",
        contentType: "application/json",
        data: JSON.stringify({"search":search}),
        success: function(result){
            if( $("#search-results").length ) {
                $("#search-results").empty()
            }
            else{
                $("#recommendations").before(
                    $("<div/>")
                    .addClass("card-columns")
                    .attr("id","search-results")
                )

                $("#search-results").before(
                    $("<div/>")
                    .addClass("col-md-12")
                    .attr("id", "search-results-header")
                       .append(
                           $("<h4/>")
                            .addClass("text-center")
                            .text("Search Results:")
                            )
                   );
            }


            for (let card of result) {
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
                $("#search-results").append(
                          $("<div/>")
                          .addClass("card h-100")
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
                                   .addClass("card-title text-center")
                                   .append(
                                       $("<a/>")
                                       .text(card["title"])
                                   )
                               )
                               .append(
                                 $("<p/>")
                                 .addClass("card-text")
                                 .attr("style","margin-top:1rem;")
                                 .text(card["description"])
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
                   }
                   if ($("#og-rex").length){}
                   else{
                       $("#recommendations").before(
                           $("<div/>")
                           .addClass("col-12")
                           .attr("id", "og-rex")
                           .append(
                               $("<h4/>")
                                .addClass("text-center")
                                .attr("style","margin-top:10%;")
                                .text("Original Recommendations:")
                                )
                       )
                   }
        }
    });
}

visualize = function(){
    if (!$("#graph").length) {
        $("#saved-recommendations")
            .before($("<div/>").attr("class", "row")
            .append(
                $("<div/>")
                .attr("class", "col-lg-9 col-md-8 col-sm-12 justify-content-center")
                .attr("style", "text-align:center;")
                .append(
                    $("<button/>")
                    .attr("class", "add-podcast-button btn btn-outline-secondary")
                    .attr("data-toggle", "modal")
                    .attr("data-target", "#d3modal")
                    .attr("title", "View graph description.")
                    .text("What is this?")
                    )
                )
                .append($("<div/>").attr("class", "col-lg-3 col-md-8 col-sm-12 justify-content-center"))
                .append(
                    $("<div/>")
                        .attr("id", "graph")
                        .attr("class", "chart justify-content-center text-center col-md-8 col-lg-9 col-sm-12"))
                .append(
                    $("<div/>")
                        .attr("id", "d3-podcast-info")
                        .attr("class", "justify-content-center text-center col-md-4 col-lg-3 col-sm-12")
                        .text("Click a circle to see more information about the podcast").fadeIn(3000)
                )
            )
            .append(
                $("<div/>")
                .attr("class", "modal fade")
                .attr("id", "d3modal")
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
                                $("<button/>")
                                .attr("class", "close")
                                .attr("data-dismiss", "modal")
                                .attr("aria-label", "Close")
                                .attr("title", "Close box")
                                .append(
                                    $("<span/>").attr("aria-hidden", "true").html("&times;")
                                )
                            )
                        )
                        .append(
                            $("<div/>").attr("class", "modal-body")
                                .append($("<p/>")
                                    .text("This graph shows how podcasts are related. Links between podcast show that at least 15 people have reviewed both podcasts. The thickness of links is a function of how many listeners are shared between podcasts, specifically: ")
                                )
                                .append($("<p/>")
                                    .append($("<code/>")
                                        .text("log(shared_listeners) - 1")
                                    )
                                )
                                .append($("<p/>")
                                     .text("Nodes size is a function of overall star rating and number of reviews:")
                                 )
                                 .append($("<p/>")
                                     .append($("<code/>")
                                         .text("log10(review_count) + star_rating")
                                     )
                                 )
                                 .append($("<p/>")
                                     .text("The nodes coloring is as follows:")
                                )
                                .append($("<img/>")
                                    .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/legend.png")
                            )
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
            setup() // from d3app.js to set up svg params
            render() // from d3app.js to render first graph
            // get graph json
            // start d3
        }
};
get_graph = function(click_pod=null, update_type=null) {
    $.post({
        url: "../graph/",
        contentType: "application/json",
        data: JSON.stringify({
            "podcasts":ids,
            "update_podcast":click_pod,
            "update_type":update_type
        }),
        success: function(result) {
            graph_data = result
            console.log(result)
        }
    });
};
