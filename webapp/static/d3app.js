// empty data object to hold d3 graph
let graph_data = []

// set margins and canvas size
const margin = {
    top: 10,
    right: 20,
    bottom: 30,
    left: 30
};
const width = 600 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

// set up canvas
let svg, link, node, g // empty vars to update when the .chart div appears

setup = function() {
    svg = d3.select('.chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .call(responsivefy)
    g = svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
        .attr('id', 'everything');

    // set up selections
    link = g.append("g")
        .attr("class", "links")
        .selectAll("line");
    node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle");

    //add zoom capabilities
    var zoom_handler = d3.zoom()
        .on("zoom", zoom_actions);
    zoom_handler(svg);
};

let div = d3.select("body").append("div")
    .attr("class", "tooltip info")
    .style("opacity", 0);

// set up color scale
const color = d3.scaleSequential()
    .domain([8, 15])
    .interpolator(d3.interpolateInferno);
const color_dict = {"liked":"#000000",
                    "recommended":"#0072b2",
                    "newly_added":"#e69f00",
                    "previously_added":"#999999"}
// set up simulation basic parameters
var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }).distance(65))
    .force("charge", d3.forceManyBody().strength(-100).distanceMin(40).distanceMax(85))
    .force("collide", d3.forceCollide())
    .force("center", d3.forceCenter(width / 2, height / 2));

function render(graph=null, update_podcast=null, update_type=null) {
    d3.json("../graph/")
        .header("Content-type","application/json; charset=UTF-8")
        .post(JSON.stringify({"podcasts":ids,
            "update_podcast": update_podcast,
            "update_type": update_type,
            "graph": graph}), function(error, graph){
                if (error) { throw error; }
                console.log(graph)
                graph_data = graph
         // node selection and data handling
        node = node
            .data(graph.nodes, function(d) { return d.id; });

        // node general update pattern
        node.exit()
            .transition()
            .duration(1500)
            .attr("r", 0)
            .remove();
        node.attr("data-status", function(d) { return update_status(d);});
        node.transition().duration(1500)
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; })
            .attr("fill", function(d) { return color_dict[d.status]; });

        node = node
            .enter().append("circle")
            .call(function(node) {
                node.transition().duration(1500)
                  .attr("r", function(d) { return d.size; })
            })
            //.attr("fill", function(d) { return color(d.pop); })
            .attr("fill", function(d) { return color_dict[d.status]; } )
            .attr("data-status", function(d) {return d.status; })
            .on("mouseover", function(d) {
                  div.transition()
                      .duration(200)
                      .style("opacity", .9);
                  var img_string = "http://podcasts-dragon-nba-who.s3-website-us-west-2.amazonaws.com/static/artwork/" + d.podcast_id + ".jpg"
                  div.html("<img src='" + img_string + "' width='80' class='tooltip-img'/>" + d.podcast_name)
                      .style("left", (d3.event.pageX) + "px")
                      .style("top", (d3.event.pageY - 28) + "px");
                  })
              .on("mouseout", function(d) {
                  div.transition()
                      .duration(500)
                      .style("opacity", 0);
              })
              .on("click", function(d){
                  update_info_sidebar(d)
              })
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .merge(node);

        // give all nodes a title with their id for hover identification
        node.append("title")
            .text(function(d) { return d.podcast_name; });

        // link selection, data handling
        link = link
            .data(graph.edges, function(d) { return d.source + "-" + d.target; });

        // link general update pattern with attrTween to keep links connected to disappearing nodes
        link
            .exit()
            .transition()
            .duration(1500)
            .attr("stroke-opacity", 0)
            .attr("stroke-width", 0)
            .attrTween("x1", function(d) {
                return function() {
                    return d.source.x;
                };
            })
            .attrTween("x2", function(d) {
                return function() {
                    return d.target.x;
                };
            })
            .attrTween("y1", function(d) {
                return function() {
                    return d.source.y;
                };
            })
            .attrTween("y2", function(d) {
                return function() {
                    return d.target.y;
                };
            })
            .remove();

        link = link
            .enter().append("line")
            .attr("stroke-width", function(d) { return d.value; })
            .merge(link);

        // add nodes and links to the siumlation
        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);
        simulation.force("link")
            .links(graph.edges);
        // restart the simulation
        simulation.alpha(1).restart();

        // set the ticked function to constantly update node and link position
        function ticked() {
            link
                .attr("x1", function(d) {
                    return d.source.x;
                })
                .attr("y1", function(d) {
                    return d.source.y;
                })
                .attr("x2", function(d) {
                    return d.target.x;
                })
                .attr("y2", function(d) {
                    return d.target.y;
                });

            node
                .attr("cx", function(d) {
                    return d.x;
                })
                .attr("cy", function(d) {
                    return d.y;
                });
        }
    });
};

// dragging functions
function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

//Zoom functions
function zoom_actions(){
    g.attr("transform", d3.event.transform)
}

update_status = function(d) {
    let attr = d.status
    if (!["recommended", "liked"].includes(attr)) {
        return "previously_added"
    } else {
        return attr
    }
}

// responsivefy from https://brendansudol.com/writing/responsive-d3
function responsivefy(svg) {
    // get container + svg aspect ratio
    const container = d3.select(svg.node().parentNode),
        width = parseInt(svg.style("width")),
        height = parseInt(svg.style("height")),
        aspect = width / height;

    // add viewBox and preserveAspectRatio properties,
    // and call resize so that svg resizes on inital page load
    svg.attr("viewBox", "0 0 " + width + " " + height)
        .attr("preserveAspectRatio", "xMinYMid")
        .call(resize);

    // to register multiple listeners for same event type,
    // you need to add namespace, i.e., 'click.foo'
    // necessary if you call invoke this function for multiple svgs
    // api docs: https://github.com/mbostock/d3/wiki/Selections#on
    d3.select(window).on("resize." + container.attr("id"), resize);

    // get width of container and resize svg to fit it
    function resize() {
        const targetWidth = Math.floor(parseInt(container.style("width"))*0.75);
        svg.attr("width", targetWidth);
        svg.attr("height", Math.round(targetWidth / aspect));
    }
}

function update_info_sidebar (podcast) {
    let itunes_string = ""
    let stitcher_string = ""
    let web_url = ""
    let button_string = ""
    if (podcast.podcast_id !== null) {
        itunes_string = $("<a/>")
            .attr("href", podcast.itunes_url)
            .attr("title", podcast.podcast_name + " at iTunes")
            .append(
                $("<img/>")
                .attr("class","podcast-link link-image")
                .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/itunes-square.png")
            )
    }
    if (podcast.stitcher_url !== null) {
        stitcher_string = $("<a/>")
            .attr("href", podcast.stitcher_url)
            .attr("title", podcast.podcast_name + " at Stitcher")
            .append(
                $("<img/>")
                .attr("class","podcast-link link-image")
                .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/stitcher-square.png")
            )
    }
    if (podcast.podcast_url !== null) {
        web_url = $("<a/>")
            .attr("href", podcast.website_url)
            .attr("title", podcast.podcast_name + " website")
            .append(
                $("<img/>")
                .attr("class","podcast-link link-icon")
                .attr("src", "https://s3-us-west-2.amazonaws.com/podcasts-dragon-nba-who/static/images/white-link.png")
            )
    }

    if (parseInt(podcast.id, 10) < 3010) {
        button_string = $("<button/>")
            .attr("id", "add-description-button")
            .attr("data-s-id", podcast.id)
            .attr("class", "btn btn-outline-secondary add-podcast-button")
            .text("Add 5 podcasts with similar descriptions")
    }
    $("#d3-podcast-info").fadeOut(250, function () { $(this).empty(); })
    setTimeout(function() {
        $("#d3-podcast-info")
            .append(
                $("<h5/>")
                    .text(podcast.podcast_name)
            )
            .append(
                $("<div/>")
                    .attr("style","display:inline-block;width:100%;")
                    .append(
                        ("<img src='http://podcasts-dragon-nba-who.s3-website-us-west-2.amazonaws.com/static/artwork/" + podcast.podcast_id + ".jpg' class='width-60' />")
                    )
                    .append(
                        $("<div/>")
                            .attr("style", "margin:auto; width:60%;")
                            .append(itunes_string)
                            .append(stitcher_string)
                            .append(web_url)
                    )
            )
            .append(
                $("<p/>")
                    .attr("class", "sidebar-description")
                    .text(podcast.description)
            )
            .append(button_string)
            .append(
                $("<button/>")
                    .attr("id", "add-listener-button")
                    .attr("data-s-id", podcast.id)
                    .attr("class", "btn btn-outline-secondary add-podcast-button")
                    .text("Add 5 podcasts with similar listeners")
            )
            .fadeIn(500)
        }, 300)
        setTimeout(function() {
            $(".add-podcast-button").on("click", more_podcasts)
        }, 1000)
}

more_podcasts = function(){
    let uid = $(this).attr("data-s-id")
    let u_type = ""
    if ($(this).attr("id") === "add-listener-button") {
        u_type = "listeners"
    } else {
        u_type = "nlp"
    }
    render(graph=graph_data, update_podcast=$(this).attr("data-s-id"), update_type=u_type)
};
