// partially from Matt Drury - https://github.com/madrury/madrury.github.io/blob/master/smoothers/js/parameter-ui.js
get_selected_parameters = function() {
    let parameters = {};
    let sliders = document.getElementsByClassName("slider");
    let slider = null;
    for(let i = 0; i < sliders.length; i++) {
            slider = sliders[i];
            parameters[slider.getAttribute("data-s-id")] = Number(slider.value);
        }
    return parameters;
};
get_selected_checkboxes = function() {
    let check_parameters = {};
    let checkboxes = document.getElementsByClassName("checkbox");
    let checkbox = null;
    for(let i = 0; i < checkboxes.length; i++) {
            checkbox = checkboxes[i];
            check_parameters[checkbox.getAttribute("data-s-id")] = (checkbox.checked);
        }
    return check_parameters;
};
get_favorites = function() {
    let fave_parameters = {};
    let favorites = document.getElementsByClassName("chosen-select-deselect");
    let favorite = null;
    for(let i = 0; i < favorites.length; i++) {
            favorite = favorites[i];
            fave_parameters[$(favorite).val()] = 5;
        }
    return fave_parameters;
};
submit = function() {
    parameters = get_selected_parameters()
    check_parameters = get_selected_checkboxes()
    fave_parameters = get_favorites()
    $.post({
        url: "/predictions/",
        contentType: "application/json",
        data: JSON.stringify({"parameters":parameters, "checkboxes":check_parameters, "favorites":fave_parameters}),
        success: function(result){
            {
                window.location.href = '/recommendations/' + result;
            };
         }
    });
}

chosen_listener = function(){
   $(".chosen-select-deselect").chosen().change(function () {
       let id = $(this).attr('id');
       var pid = $("#" + id).val();
       $.post({
           url: "/dd-update/",
           contentType: "application/json",
           data: JSON.stringify({"podcast":pid}),
           success: function(result){
               $("#" + id + "-updated").empty()
               if (result["action"] === "populate") {
                   $("#" + id + "-updated").append(
                        $("<a/>")
                        .attr("href", "#")
                           .append(
                               $("<img/>")
                                .attr("src", "http://podcasts-dragon-nba-who.s3-website-us-west-2.amazonaws.com/static/artwork/"+result["podcast_art_id"]+".jpg")
                                .attr("style","margin-top:1rem;")
                                .addClass("card-img-top")
                                )
                       );
                   $("#" + id + "-updated").append(
                       $("<div/>")
                       .append(
                           $("<p/>")
                           .addClass("card-text")
                           .attr("style","margin-top:1rem;")
                           .text(result["podcast_description"])
                       )
                   );
               }
               else {
               }
           }
       });
       let curr_selects = $(".chosen-select-deselect")
       let update_flag = true
       //console.log(update_flag)
       for (let select_menu of curr_selects) {
           //console.log($(select_menu).val())
           if ($(select_menu).val() === "") {
               update_flag = false
           }
           else {
           }
       }
       //console.log(update_flag)
       if (update_flag === true) {
           new_favorite_podcast()
       }
       else {
       }
   });
};

$(".chosen-select-deselect").chosen().change(function () {
      var id = $(this).attr('id');
      //console.log(id);
});
var div_counter = 0;
new_favorite_podcast = function() {
   div_counter++
   let curr_div_id = "fave"+div_counter
   $("#favorites-row").append(
       $("<div/>")
         .addClass("col-lg-3 col-md-4 col-sm-6 portfolio-item")
         .append(
           $("<div/>")
           .addClass("card h-100")
           .append(
             $("<a/>")
               .attr("href","#")
           )
           .append(
             $("<div/>")
               .addClass("card-body")
           .append(
             $("<h4/>")
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
                   .attr("id",curr_div_id)
                   .attr("data-placeholder", "Choose a podcast..")
                   .attr("tabindex","2")
                   .attr("style","width:100%;")
                   .addClass("chosen-select-deselect")
                   .append(
                     $("<option/>")
                       .attr("value","")
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
   $("#"+curr_div_id).chosen({allow_single_deselect: true});
   populate_dropdown(curr_div_id)
   chosen_listener()
   //console.log(curr_div_id)
}

populate_dropdown = function(id) {
   $.getJSON("../static/data/podcast_pid_list.json", function(data) {
       $.each(data, function(key, value) {
           $("#"+id).append($("<option />").val(value[0]).text(value[1]));
       });
       $("#"+id).trigger("chosen:updated");
   });
}

chosen_listener()
