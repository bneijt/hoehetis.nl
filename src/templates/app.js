
function app() {


    var context = cubism.context()
        .serverDelay(new Date(2012, 4, 2) - Date.now())
        .step(50e5)
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

    d3.select("body").selectAll(".horizon")
        .data(["Doden", "Gevonden", "Verloren", "Vergeten"].map(random))
        .enter().insert("div", ".bottom")
        .attr("class", "horizon")
        .call(context.horizon()
        .height(120)
        .extent([-10, 10]));


    d3.select("body").append("div")
        .attr("class", "rule")
        .call(context.rule());



    context.on("focus", function(i) {
        d3.selectAll(".value").style("right", i == null ? null : context.size() - i + "px");
    });


    function random(name) {
        var value = 0,
            values = [],
            i = 0,
            last;
        return context.metric(function(start, stop, step, callback) {
                start = +start, stop = +stop;
                if (isNaN(last)) {
                    last = start;
                }
                while (last < stop) {
                    last += step;
                    value = Math.max(-10, Math.min(10, value + .8 * Math.random() - .4 + .2 * Math.cos(i += .2)));
                    values.push(value);
                }
                callback(null, values = values.slice((start - stop) / step));
            }, name);
        }

}
