
graph = {};
selectedEdge = null;
selectedNode = null;
numGraphs = null;

var svg = d3.select('#graph-col')
    .append('svg')
    .attr('class', 'graph')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('id', 'main-svg');

var backRect = svg.append('rect')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', 'red')
    .attr('fill-opacity', 0);

var padLayouts = function(layout) {
	var whalf = svgWidth()/2;
	var hhalf = svgHeight()/2;
	var nrad = rad5();
	var pad = nrad * 2;

	var padded = layout.map(function(coords) {
		var x = coords[0];
		var y = coords[1];
		var nx = x * (whalf - pad) + whalf;
		var ny = y * (hhalf - pad) + hhalf;
		return [nx, ny];
	});

	return padded;
}


var redraw = function() {
	drawGraphPadded(svg, graph.nodes, graph.edges, graph.layout);
}

var initGraphData = function() {
	var dataPane = d3.select('#graph-data-col')

	dataPane.append('h4')
		.attr('id', 'graph-data-title-p')
		.attr('align', 'center')
		.text('Graph Data');

	dataPane.append('p')
		.attr('id', 'rank-p');
		
	dataPane.append('p')
		.attr('id', 'dist-p');

	dataPane.append('p')
		.attr('id', 'num-species-p');
	
	dataPane.append('p')
		.attr('id', 'num-edges-p');
}

var updateGraphData = function() {

	d3.select('#rank-p')
		.text('Rank: ' + graph.rank);
		
	d3.select('#dist-p')
		.text('Distance: ' + graph.dist);
	
	d3.select('#num-edges-p')
		.text(graph.edges.length + ' Edges');

	d3.select('#num-species-p')
		.text(graph.nodes.length + ' Species');
}

var initInfoPane = function() {
	var infoPane = d3.select('#data-col')

	infoPane.append('h4')
		.attr('id', 'node-title-p')
		.attr('align', 'center')
		.style('display', 'none');

	infoPane.append('h4')
		.attr('id', 'edge-title-p')
		.attr('align', 'center')
		.style('display', 'none');

	infoPane.append('h5')
		.attr('id', 'edge-inter-p')
		.attr('align', 'center')
		.style('display', 'none');

	infoPane.append('pre')
		.attr('id', 'default-info-p')
		.style('margin', '10px')
		.style('white-space', 'normal')
		.style('word-break', 'normal')
		.style('background-color', 'grey')
		.style('color', 'white')
		.text("This is the graph inspector. Click on a node or edge to see information about its parameters in this pane. The pane below contains statistics about this graph. Change the graph being viewed with the navigation bar below the graph.");
}


var updateInfoPane = function(params) {
	var pane = d3.select('#data-col');
	var oldPars = pane.selectAll('.param')
		.data(params);

	oldPars.exit()
		.remove();

	var newPars = pane.selectAll('.param')
		.data(params)
		.enter()
		.append('pre')
		.attr('class', 'param');

	var allPars = pane.selectAll('.param')
		.text(function(d) {
			return 'Parameter Type: ' + d.paramType + '\n'
					+ 'Value: ' + d.val + '\n'
					+ 'Bounds: (' + d.bounds + ')';
		});
}

var clearInfoPane = function() {
	updateInfoPane([]);
	d3.select('#edge-title-p')
		.style('display', 'none');
	d3.select('#node-title-p')
		.style('display', 'none');
	d3.select('#edge-inter-p')
		.style('display', 'none');
	d3.select('#default-info-p')
		.style('display', 'none');
}


var clearHighlights = function() {
	d3.selectAll('.edge-hover')
		.attr('stroke-opacity', 0)
		.on('mouseout', function() {
			d3.select(this).attr('stroke-opacity', 0);
		}); 
	d3.selectAll('.node')
		.attr('stroke-width', 0);

	d3.selectAll('.edge')
		.attr('opacity', e => e.complex ? 0.5 : 1);

	selectedEdge = null;
	selectedNode = null;
}

var clearInfoAndHighlights = function() {
	clearHighlights();
	clearInfoPane();
	//defaultPane();
}

var clearAndDefault = function() {
	clearInfoAndHighlights();
	defaultPane();
}

var highlightSelected = function() {
	if (selectedEdge != null) {
		d3.selectAll('.edge-hover')
			.filter(e => e.from == selectedEdge.from && e.to == selectedEdge.to)
			.attr('stroke-opacity', 0.5)
			.on('mouseout', null);
		highlightComplexPath(selectedEdge);
	}
	else if (selectedNode != null) {
		d3.selectAll('.node')
			.filter(n => n.id == selectedNode.id)
			.attr('stroke-width', 10)
			.attr('stroke', 'black');
		highlighAttached(selectedNode);
	}
}

var highlighAttached = function(n) {
	var alledges = d3.selectAll('.edge')
		.attr('opacity', 0.1);
	var attachedEdges = d3.selectAll('.edge')
		.filter(function(e) {
			var to = e.to == n.id;
			var complex = e.complex ? e.complexTo : false;
			return to || complex;
		})
		//.each(e => highlightComplexPath(e))
		.attr('opacity', e => e.complex ? 0.5 : 1);
	var attachedHovers = d3.selectAll('.edge-hover')
		.filter(function(e) {
			var to = e.to == n.id;
			return to;
		})
		.attr('stroke-opacity', 0.5)
		.on('mouseout', null)
}

var highlightComplexPath = function(e) {
	console.log('highlight cplx path')
	if (e.interactome || e.complex) {
		var pathEdges = e.interactome ? e.interactome.map(n => [n, e.from]) : e.complex.map(n => [n, e.to]).concat([[e.to, e.complexTo]]);
		d3.selectAll('.edge')
			.filter(function (ed) {
				var thisEdge = ed.from == e.from && ed.to == e.to;
				var onPath = pathEdges.map(pe => ed.from == pe[0] && pe[1] == ed.to).reduce((a,b) => a || b);
				return !(thisEdge || onPath);
			})
			.attr('opacity', 0.1);
		
		d3.selectAll('.edge-hover')
			.filter(ed => pathEdges.map(pe => ed.from == pe[0] && pe[1] == ed.to).reduce((a,b) => a || b))
			.attr('stroke-opacity', 0.5)
			.on('mouseout', null);
	}
}

var updateNodeData = function(n) {
	clearInfoAndHighlights();
	selectedNode = n;
	highlightSelected();
	d3.select('#edge-title-p')
		.style('display', 'none');
	d3.select('#edge-inter-p')
		.style('display', 'none');
	d3.select('#node-title-p')
		.style('display', 'block')
		.text(n.complex ? 'Node [' + n.complex + ']' : 'Node ' + n.id);
	updateInfoPane(n.parameters);
}

var updateEdgeData = function(e) {
	clearInfoAndHighlights();
	selectedEdge = e;
	highlightSelected();
	var edgeTitle = 'Edge ' + e.from + ', ' + e.to;
	if (e.interactome) {
		edgeTitle = 'Edge [' + e.interactome + '], ' + e.to;
	}
	else if (e.complex) {
		edgeTitle = 'Edge [' + e.complex + '], ' + e.complexTo;
	}
	d3.select('#edge-title-p')
		.style('display', 'block')
		.text(edgeTitle);
	d3.select('#edge-inter-p')
		.style('display', 'block')
		.text('Interaction type ' + e.interaction);
	d3.select('#node-title-p')
		.style('display', 'none');

	var params = e.complex ? d3.selectAll('.edge').filter(ed => ed.from == e.to && ed.to == e.complexTo).data()[0].parameters : e.parameters;
	updateInfoPane(params);
}

// Nav button functions:
var updateNavs = function() {
	if (numGraphs == null) {
		d3.json('/num-graphs', function(n) {
			numGraphs = n;
		})
	}
	document.getElementById('cur-page').value = graph.rank;
    d3.select('#back-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(Math.max(graph.rank -1, 0));
        });
    d3.select('#next-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(Math.min(graph.rank +1, numGraphs-1));
        });
    d3.select('#first-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(0);
        });

    d3.select('#last-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(numGraphs-1);
        });
    $('#cur-btn').text(graph.rank);
}


var getGraph = function(gnum) {
	d3.json('/graph/' + gnum, function(d) {
		if (d) {
			graph = d;
		  	redraw();
		  	updateGraphData();
		  	nodeOnClick(updateNodeData);
			edgeOnClick(updateEdgeData);
			updateNavs();
		}
			
	})
}

var goToGraph = function(event) {
	var to = document.getElementById('cur-page').value;
	// Check if to is a number
	if (to % 1 === 0) {
		getGraph(to);
	}
}

var defaultPane = function() {
	clearInfoPane();
	d3.select('#default-info-p')
		.style('display', 'block');
}



window.addEventListener('resize', redraw);
$('#cur-page').keypress(
	function(event) {
		if (event.which == 13) {
			event.preventDefault();
			$('#go-btn').trigger('click');
		}
	});
initGraphData();
initInfoPane();
backRect.on('click', clearAndDefault);
getGraph(0);




