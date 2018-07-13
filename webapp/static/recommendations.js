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
