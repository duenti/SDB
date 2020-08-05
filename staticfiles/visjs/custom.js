var network

  function draw() {
	  var nodesDataset = new vis.DataSet(nodes); // these come from WorldCup2014.js
	  var edgesDataset = new vis.DataSet(edges); // these come from WorldCup2014.js

	  // create a network
	  var container = document.getElementById('mynetwork');
	  var data = {
	    nodes: nodesDataset,
	    edges: edgesDataset
	  };
	  
	  network = new vis.Network(container, data, options);

	  network.on("stabilizationProgress", function(params) {
        var maxWidth = 496;
        var minWidth = 20;
        var widthFactor = params.iterations/params.total;
        var width = Math.max(minWidth,maxWidth * widthFactor);

        //document.getElementById('bar').style.width = width + 'px';
        document.getElementById('bar').style.width = Math.round(widthFactor*100) + '%';
        document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';
    });
    network.once("stabilizationIterationsDone", function() {
        document.getElementById('text').innerHTML = '100%';
        document.getElementById('bar').style.width = '100%';
        document.getElementById('loadingBar').style.opacity = 0;
        // really clean the dom element
        setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 500);
    });

    network.on("stabilizationIterationsDone", function () {
    	network.setOptions( {
            physics: false,
            nodes: {
              shape: 'dot',
              scaling: {
                customScalingFunction: function (min,max,total,value) {
                  return value/total;
                },
                min:5,
                max:150
              }
            }
        } );
  	});

		//network.freezeSimulation(true);
  }

  function draw_home() {
    var nodesDataset = new vis.DataSet(nodes); // these come from WorldCup2014.js
    var edgesDataset = new vis.DataSet(edges); // these come from WorldCup2014.js

    // create a network
    var container = document.getElementById('mynetwork');
    var data = {
      nodes: nodesDataset,
      edges: edgesDataset
    };
    
    network = new vis.Network(container, data, options);

    network.on("stabilizationProgress", function(params) {
        var maxWidth = 496;
        var minWidth = 20;
        var widthFactor = params.iterations/params.total;
        var width = Math.max(minWidth,maxWidth * widthFactor);

        //document.getElementById('bar').style.width = width + 'px';
        document.getElementById('bar').style.width = Math.round(widthFactor*100) + '%';
        document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';
    });
    network.once("stabilizationIterationsDone", function() {
        document.getElementById('text').innerHTML = '100%';
        document.getElementById('bar').style.width = '100%';
        document.getElementById('loadingBar').style.opacity = 0;
        // really clean the dom element
        setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 500);
    });

    network.on("stabilizationIterationsDone", function () {
      network.setOptions( { physics: false } );
      zoom();
    });

    //network.freezeSimulation(true);
  }

  function scaleHubsize(type){
    if(type){
        network.setOptions(
            {nodes: {
              shape: 'dot',
              scaling: {
                customScalingFunction: function (min,max,total,value) {
                  return value/total;
                },
                min:5,
                max:150
              }
            }
        });
    }else{
        network.setOptions({nodes: {shape: 'ellipse'}});
    }
  }
  
  function zoom(){
    network.focus(1, {scale: 0.5});
  }

  function scaleEdgeByProb(type){
	for(var i = 0; i < edges.length; i++){
		var edge = edges[i];
		if(type)
			edge.value = edge.pvalue;
		else
			delete edge.value;
		edge.title = edge.pvalue;
	}
  }

  function scaleEdgeByCorr(type){
	for(var i = 0; i < edges.length; i++){
		var edge = edges[i];
		if(type)
			edge.value = edge.correlation;
		else
			delete edge.value;
		edge.title = edge.correlation;
	}
  }
  
  function colorByComm(type){
	  for(var i = 0; i < nodes.length; i++){
		  var node = nodes[i];
		  if(type)
			  node.color = node.commColor;
		  else
			  delete node.color;
	  }
  }
  
  //network.on("hoverEdge", function (params) {
  //    console.log('hoverEdge Event:', params.weight);
  //});