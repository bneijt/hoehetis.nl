

function app() {
    d3.json("graphs.json", function(error, json){
        renderGraphs(json);
    });
}

function renderGraphs(graphs) {
    var context = cubism.context()
        .step(60*60*1000)
        .size(1280)
        .stop();

    d3.select("#hoehetis")
        .append("div")
        .attr("class", "axis")
        .call(context.axis().orient("top"));

    d3.select("#hoehetis").selectAll(".axis")
        .data(["top", "bottom"])
        .enter().append("div")
        .attr("class", function(d) { return d + " axis"; })
        .each(function(d) { d3.select(this).call(context.axis().orient(d)); });

    d3.select("#hoehetis").selectAll(".horizon")
        .data(d3.keys(graphs).sort().map(metricForGraph))
        .enter()
        .insert("div", ".bottom")
        .attr("class", "horizon")
        .call(context.horizon()
            .height(80)
            .extent([0, 100])
            );


    d3.select("#hoehetis").append("div")
        .attr("class", "rule")
        .call(context.rule());


    function metricForGraph(name) {
        return context.metric(function(start, stop, step, callback) {
                callback(null, graphs[name].slice((start - stop) / step));
            }, name);
        }
}
