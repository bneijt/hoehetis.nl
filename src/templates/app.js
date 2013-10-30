

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

    d3.select("#demo")
        .append("div")
        .attr("class", "axis")
        .call(context.axis().orient("top"));

    d3.select("body").selectAll(".axis")
        .data(["top", "bottom"])
        .enter().append("div")
        .attr("class", function(d) { return d + " axis"; })
        .each(function(d) { d3.select(this).call(context.axis().ticks(12).orient(d)); });

    function mkHorizon() {
        return context.horizon()
            .height(120)
            .extent([0, 100]);
        }
    d3.select("body").selectAll(".horizon")
        .data(d3.keys(graphs).sort().map(metricForGraph))
        .enter()
        .insert("div", ".bottom")
        .attr("class", "horizon")
        .call(mkHorizon());


    d3.select("body").append("div")
        .attr("class", "rule")
        .call(context.rule());



    context.on("focus", function(i) {
        d3.selectAll(".value").style("right", i == null ? null : context.size() - i + "px");
    });


    function metricForGraph(name) {
        return context.metric(function(start, stop, step, callback) {
                callback(null, graphs[name].slice((start - stop) / step));
            }, name);
        }
}
