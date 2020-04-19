function draw_hm(target, data, i){
      var residues = data["residues"];
      var residues_conservation = residues.slice();
      residues_conservation.unshift("");
      residues_conservation.unshift("Conservation");
      var matrix = data["data"];
      var num = matrix.length;

      var width = (num+2)*40;
      var height = num*40;
      //create svg
      var thisg = "thisg" + i;
      var thisg_id = "#" + thisg;
      var thissvg = "thissvg" + i;
      var thissvg_id = "#" + thissvg;

      $(target).empty();

      var svg = d35.select(target).append("svg")
                                 .attr("width", width+10)
                                 .attr("height", height)
                                 .attr("id", thissvg)
                                //  .style("margin-left", -margin.left + "px")
                                 .append("g")
                                 .attr("id", thisg);
                                 //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

     svg.append("rect")
        .attr("class", "background")
        .attr("width", width)
        .attr("height", height)
        .style("fill-opacity", 0);

      //create data
      //Passei pra data.js

      //var numcols = matrix[0].length;
      //create x and y scales
      var x = d35.scaleBand()
                .domain(d35.range(num+2))
                .range([0, width]);

      var y = d35.scaleBand()
                .domain(d35.range(num))
                .range([0, height]);

      //create color scaling
      var colorMap = d35.scaleLinear()
                             .domain([-1, 0, 0.5, 1])
                             .range(["white", "red", "yellow", "green"]);

      var row = svg.selectAll(".row")
                   .data(matrix)
                   .enter().append("g")
                   .attr("class", "row")
                   .attr("transform", function(d, i) { return "translate(0," + y(i) + ")"; });

      row.selectAll(".cell")
         .data(function(d) { return d; })
         .enter().append("rect")
         .attr("class", "cell")
         .attr("x", function(d, i) {
          //  console.log(i);
          //  console.log(x(i));
          //  console.log(this);
           return x(i);
         })
         .attr("width", x.bandwidth())
         .attr("height", y.bandwidth())
         .style("stroke-width", 0);

      row.selectAll("text")
         .data(function(d) { return d; })
         .enter()
         .append("text")
         .attr("x", function(d, i) {return x(i) - x.bandwidth()/2 + x.bandwidth();})
         .attr("y", y.bandwidth() / 2)
         .attr("dy", ".32em")
         .attr("text-anchor", "middle")
         .text(function(d) {
           if (d > 0) {
             return d;
           } else {
             return "";
           }
         })
         //text resizing to fit
         .style("font-size", function(d) {
          if (this.getComputedTextLength() > x.bandwidth()) {
            return (x.bandwidth() - 8) / this.getComputedTextLength() * 20 + "px";
          }
         });

      row.append("line")
         .attr("x2", width);

      row.selectAll(".cell")
         .data(function(d, i) { return matrix[i]; })
         .style("fill", function(d,i) {
          if (d == -1) {
            return "transparent";
          }
          return colorMap(d);
         });


      //maximum possible text size calculation...
      var wh = {h:-1, w:-1, bottom:-1, right:-1,top:-1};
      Array.from(document.querySelectorAll('rect.cell')).map(function(ele) {
        var bbox = ele.getBoundingClientRect();
        // console.log(ele);
        // console.log(bbox);
        wh.w = (wh.w<bbox.width) ? bbox.width :wh.w;
        wh.h = (wh.h<bbox.height) ? bbox.height :wh.h;
        wh.bottom = (wh.bottom<bbox.bottom) ? bbox.bottom :wh.bottom;
        wh.top = (wh.top<bbox.top) ? bbox.top :wh.top;
        wh.right = (wh.right<bbox.right) ? bbox.right :wh.right;
      });
      var maximum_text_width = width - wh.right;
      var maximum_text_height = height - wh.bottom;

      row.append("text")
         .attr("x", -16)
         .attr("y", y.bandwidth() / 2)
         .attr("dy", ".32em")
         .attr("text-anchor", "end")
         .attr("class", "rowtext")
         .text(function(d, i) { return residues[i]; })
         //text resizing to fit
        //  .style("font-size", function(d) {
        //   if (this.getComputedTextLength() > maximum_text_width) {
        //     return (maximum_text_width - 8) / this.getComputedTextLength() * 10 + "px";
        //   }
        //  })
         ;

         var column = svg.selectAll(".column")
                      .data(residues_conservation)
                      .enter().append("g")
                      .attr("class", "column")
                      .attr("transform", function(d, i) { return "translate(" + x(i) + ")rotate(-90)"; });

      column.append("line")
            .attr("x1", -width);

      column.append("text")
            .attr("x", 16)
            .attr("y", y.bandwidth() / 2)
            .attr("dy", ".32em")
            .attr("class", "coltext")
            .attr("text-anchor", "start")
            .text(function(d, i) { return d; })
            // .style("font-size", function(d) {
            //   console.log(this.getComputedTextLength());
            //   console.log(maximum_text_height);
            //  if (this.getComputedTextLength() > maximum_text_height) {
            //    return (maximum_text_width - 8) / this.getComputedTextLength() * 10 + "px";
            //  }
            // })
            ;
      // automatic svg resizing AFTER text insertion
      var wh = {w:-1,h:-1};
      Array.from(document.querySelectorAll('text.rowtext')).map(function(ele) {
        var bbox = ele.getBoundingClientRect();
        wh.w = (wh.w<bbox.width) ? bbox.width :wh.w;
      });
      Array.from(document.querySelectorAll('text.coltext')).map(function(ele) {
        var bbox = ele.getBoundingClientRect();
        wh.h = (wh.h<bbox.height) ? bbox.height :wh.h;
      });
      d35.select(thisg_id).attr("transform", "translate(" + (wh.w + 24) + "," + (wh.h + 24) + ")");
      var g_width = d35.select(thisg_id).node().getBoundingClientRect().width;
      var svg_width = d35.select(thissvg_id).node().getBoundingClientRect().width;
      var g_height = d35.select(thisg_id).node().getBoundingClientRect().height;
      var svg_height = d35.select(thissvg_id).node().getBoundingClientRect().height;
      if (g_width > svg_width) {
        d35.select(thissvg_id).attr("width", g_width + 20);
      }
      if ( (g_height) > svg_height) {
        d35.select(thissvg_id).attr("height", g_height);
      }

     //Ajust size
     $(thissvg_id).width($(thissvg_id).width()+10)
}

function wrap(text, width) {
        text.each(function() {
          var text = d35.select(this),
              words = text.text().split(/\s+/).reverse(),
              word,
              line = [],
              lineNumber = 0,
              lineHeight = 1.1, // ems
              y = text.attr("y"),
              dy = parseFloat(text.attr("dy")),
              tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
          while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
              line.pop();
              tspan.text(line.join(" "));
              line = [word];
              tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
            }
          }
        });
      }