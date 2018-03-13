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
                                   $("<a/>")
                                   .attr("href", card["itunes_url"])
                                   .append(
                                       $("<img/>")
                                       .attr("style","width:30%; display:inline; padding-bottom:2.5%; margin-right:2.75%")
                                       .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/itunes-square.png")
                                   )
                               )
                               .append(
                                   $("<a/>")
                                   .attr("href", card["stitcher_url"])
                                   .append(
                                       $("<img/>")
                                       .attr("style","width:30%; display:inline; padding-bottom:2.5%; margin-right:2.75%")
                                       .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/stitcher-square.png")
                                   )
                               )
                               .append(
                                   $("<a/>")
                                   .attr("href", card["podcast_url"])
                                   .append(
                                       $("<img/>")
                                       .attr("style","width:30%; display:inline; padding:5%; margin-top:-1%;background-color:#006c7d;border-radius:10px")
                                       .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/white-link.png")
                                   )
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

$('#text-search').keypress(function(e){
    if(e.which == 13){//Enter key pressed
        $('#search-button').click();//Trigger search button click event
    }
});
