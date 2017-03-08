var transition_duration = 700;
var edge_duration = transition_duration/2;
var edge_delay = transition_duration / 2;
var hover_width = 15;
var allColors = d3.schemeCategory10;
var curColorPos = 0;
var cur_color = 'teal';
var markerSide = 4;

var svgWidth = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).width()
}
var svgHeight = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).height()
}
var rad5 = function(svg) {
	return Math.floor(Math.min(svgWidth(svg), svgHeight(svg)) * 0.05);
}
var radx = function(x, svg) {
	return Math.floor(Math.min(svgWidth(svg), svgHeight(svg)) * x);
}
var getRandColor = function() {
	var colors = d3.schemeCategory10;
	var i = Math.floor(Math.random() * colors.length);
	return i;
}
var randColor = function() {
	var colors = d3.schemeCategory10;
	var i = Math.floor(Math.random() * colors.length);
	cur_color= colors[i];
}

var nextColor = function() {
	cur_color = allColors[curColorPos];
	curColorPos++;
	if (curColorPos >= allColors.length) {
		curColorPos = 0;
	}
}



// Define arrow endings for edges
var arrowHead = null;
    
var initArrowHead = function(svg) {
	arrowHead = svg.append('marker')
	    .attr('id', 'arrow-head')
	    .attr('orient', 'auto')
	    .attr('refX', 0.1)
	    .attr('refY', 2)
	    .attr('markerWidth', 4)
	    .attr('markerHeight', 4);

	arrowHead.append('path')
	    .attr('d', 'M 0 0 V ' + markerSide +'L ' + markerSide + ' ' + markerSide/2 + ' Z')
	    .attr('fill', 'black');
}


var line_shorten = function(a, b, d, strWidth) {
   var dx = b[0] - a[0];
   var dy = b[1] - a[1];
   var dist = Math.sqrt(dx*dx + dy*dy);
   var arrGap = strWidth*markerSide;
   var start_ratio = d / dist;
   var end_ratio = (d + arrGap) / dist;

   var x1 = dx * start_ratio + a[0];
   var y1 = dy * start_ratio + a[1];

   var x2 = dx - dx*end_ratio + a[0];
   var y2 = dy - dy*end_ratio + a[1];

   return [[x1, y1], [x2, y2]];
 }

var calcStrWidth = function(d, edgeScale) {
	occ = d.occurrences;
	if (!occ) {
		occ = 4;
	}
	var strScale = edgeScale(occ)/500;
	var minSide = Math.min(svgWidth(svg), svgHeight(svg));
	var strWidth = minSide * strScale;
	return strWidth;
}

var update_edge_hovers = function(lines, layout, node_radius, edgeScale) {
	lines.transition()
    .duration(transition_duration/4)
    .attr('stroke', cur_color)
    .attr('stroke-width', 0)
    .transition()
    .duration(0)
    .attr('x1', function(d, i) {
    	return layout[d.from][0];
    })
    .attr('y1', function(d, i) {
    	return layout[d.from][1];
    })
    .attr('x2', function(d, i) {
    	return layout[d.from][0];
    })
    .attr('y2', function(d, i) {
    	return layout[d.from][1];
    })
    .transition()
	.duration(edge_duration)
	.delay(edge_delay)
	.attr('x1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[1][1];
	})
    .attr('stroke-width', hover_width);

    lines.select('title')
    	.text(function(d, i) {
            return 'Edge = (' + d.from + ', ' + d.to + ')';
        });
}

var updateLineEdges = function(lines, layout, node_radius, edgeScale) {

	lines.transition()
	.duration(transition_duration/4)
	.attr('opacity', 0)
	.attr('stroke-width', function(d) {
		return calcStrWidth(d, edgeScale);
	})
	.transition()
	.duration(0)
	.attr('x1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][1];
	})
	.transition()
	.duration(edge_duration)
	.delay(edge_delay)
	.attr('x1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(d, edgeScale));
	    return pos[1][1];
	})
	.attr('opacity', 1);

	lines.select('title')
		.text(function(d, i) {
	        return 'Edge = (' + d.from + ', ' + d.to + ')';
	    });
}


var draw_edge_hovers = function(svg, edges, layout, node_radius, edgeScale) {
	// Grab edge-hovers that need to vanish and update
	var done_edge_hovers = svg.selectAll('line.edge-hover')
		.data(edges)
		.exit()
		.remove();

	// Create new edge hovers 
	var new_edge_hovers = svg.selectAll('line.edge-hover')
		.data(edges)
		.enter()
	    .append('line')
		.attr('class', 'edge-hover')
	    .attr('stroke', cur_color)
	    .attr('stroke-width', 0)
	    .attr('stroke-opacity', 0)
	    .attr('x1', svgWidth(svg)/2)
	    .attr('y1', svgHeight(svg)/2)
	    .attr('x2', svgWidth(svg)/2)
	    .attr('y2', svgHeight(svg)/2)
	    .on('mouseover', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0.5);
	    })
	    .on('mouseout', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0)
	    });

	new_edge_hovers.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d.from + ', ' + d.to + ')';
	    });

	// Grab existing edge hovers and update
	var all_hovers = svg.selectAll('line.edge-hover')
		.data(edges);
	update_edge_hovers(all_hovers, layout, node_radius, edgeScale);
}


var drawLineEdges = function(svg, edges, layout, node_radius, edgeScale) {

	if (arrowHead == null) {
		initArrowHead(svg);
	}

	// Grab edges that need to vanish and update
	var done_edges = svg.selectAll('line.edge')
		.data(edges)
		.exit()
		.transition()
		.duration(transition_duration)
		.attr('x1', svgWidth(svg)/2)
	    .attr('y1', svgHeight(svg)/2)
	    .attr('x2', svgWidth(svg)/2)
	    .attr('y2', svgHeight(svg)/2)
		.attr('stroke-opacity', 0)
		.attr('marker-end', null)
		.remove();

	// Create new edges
	var new_edges = svg.selectAll('line.edge')
		.data(edges)
		.enter()
		.append('line')
		.attr('class', 'edge')
	    .attr('stroke', 'black')
	    .attr('stroke-width', function(d) {
	    	return calcStrWidth(d, edgeScale);
	    })
	    .attr('marker-end', 'url(#arrow-head)')
	    .attr('x1', svgWidth(svg)/2)
	    .attr('y1', svgHeight(svg)/2)
	    .attr('x2', svgWidth(svg)/2)
	    .attr('y2', svgHeight(svg)/2)
	    .attr('opacity', 0);

	new_edges.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d.from + ', ' + d.to + ')';
	    });

	// Grab all edges
	var all_edges = svg.selectAll('line.edge')
		.data(edges);

	updateLineEdges(all_edges, layout, node_radius, edgeScale);

}

var circlePathInterp = function(path, layout, node_radius) {
	// Factory
	return function(d, i) {
		if (d.from < layout.length) {
			var xMax = layout[d.from][0] + node_radius * Math.cos(0.5) + 10;
			var yMax = layout[d.from][1] - node_radius * Math.sin(0.5) - 10;

			var x1 = layout[d.from][0] + node_radius * Math.cos(0.5);
			var y1 = layout[d.from][1] + node_radius * Math.sin(0.5);

			var drx = node_radius;
			var dry = node_radius;

			var xrot = 0;

			var largeArcFlag = 1;
			var sweepFlag = 0;

			var sweepArray = Array.from(Array(50).keys())
				.map(a => (a+1)/50)
				.map(a => a*path.getTotalLength())
				.map(a => path.getPointAtLength(a))
				.map((a, ind) => 'M' + x1 + ' ' + y1 + ' A' + drx*(ind/50) + ' ' + dry*(ind/50) + ', ' + xrot + ',' + largeArcFlag + ', ' + sweepFlag + ', ' + a.x + ' ' + a.y);
			
			// Interp
			return d3.scaleQuantile()
				.domain([0,1])
				.range(sweepArray);
		}
	}
}

var updateSelfEdgeHovers = function(paths, layout, node_radius, edgeScale) {
	var numNodes = layout.length;
	var step = 360 / numNodes;
	paths.attr('stroke', cur_color)
	    .attr('stroke-width', 0)	
		.attr('transform', function(d, i) {
			var node = d.from; 
			if (node < layout.length) {
				return 'rotate(' + (step*node) 
								 + ' ' 
								 + layout[d.from][0]
								 + ' ' 
								 + layout[d.from][1]
								 + ')';
			}
			
		}) 
		.attr('d', function(d, i) {
			if (d.from < layout.length) {
				var x1 = layout[d.from][0] + node_radius * Math.cos(0.5);
				var y1 = layout[d.from][1] + node_radius * Math.sin(0.5);

				var arrGap = (calcStrWidth(d, edgeScale) * markerSide * 10/16);
				var x2 = layout[d.from][0] + node_radius * Math.cos(0.5); 
				var y2 = layout[d.from][1] - node_radius * Math.sin(0.5); 
				if (!d.occurrences) {
					x2 += arrGap;
					y2 -= arrGap;
				}

				var drx = node_radius;
				var dry = node_radius;

				var xrot = 0;

				var largeArcFlag = 1;
				var sweepFlag = 0;

				return 'M' + x1 + ' ' + y1 + ' A' + drx + ' ' + dry + ', ' + xrot + ',' + largeArcFlag + ', ' + sweepFlag + ', ' + x2 + ' ' + y2;	
			}
		})
		.transition()
		.duration(transition_duration )
		.delay(edge_delay)
		.attrTween('d', function(d, i) {
			return circlePathInterp(d3.select(this).node(), layout, node_radius)(d, i);
		}) 
		.attr('stroke-width', hover_width);

	paths.select('title')
		.text(function(d, i) {
		    return 'Edge = (' + d.from + ', ' + d.to + ')';
		});
}



var drawSelfEdgeHovers = function(svg, edges, layout, node_radius, edgeScale) {
	// Grab edge-hovers that need to vanish and update
	var done_edge_hovers = svg.selectAll('path.edge-hover')
		.data(edges)
		.exit()
		.remove();

	// Create new edge hovers 
	var new_edge_hovers = svg.selectAll('path.edge-hover')
		.data(edges)
		.enter()
	    .append('path')
		.attr('class', 'edge-hover')
	    .attr('stroke', cur_color)
	    .attr('stroke-width', 0)
	    .attr('stroke-opacity', 0)
	    .attr('fill', 'transparent')
	    .on('mouseover', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0.5);
	    })
	    .on('mouseout', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0)
	    });

	new_edge_hovers.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d.from + ', ' + d.to + ')';
	    });

	// Grab existing edge hovers and update
	var all_hovers = svg.selectAll('path.edge-hover')
		.data(edges);

	updateSelfEdgeHovers(all_hovers, layout, node_radius, edgeScale);
}

var updateSelfEdges = function(paths, layout, node_radius, edgeScale) {
	var numNodes = layout.length;
	var step = 360 / numNodes;
	paths.attr('opacity', 0)
		.attr('stroke-width', d => calcStrWidth(d, edgeScale))		
		.attr('transform', function(d, i) {
			var node = d.from; 
			if (node < layout.length) {
				return 'rotate(' + (step*node) 
								 + ' ' 
								 + layout[d.from][0]
								 + ' ' 
								 + layout[d.from][1]
								 + ')';
			}
			
		}) 
		.attr('d', function(d, i) {
			if (d.from < layout.length) {
				var x1 = layout[d.from][0] + node_radius * Math.cos(0.5);
				var y1 = layout[d.from][1] + node_radius * Math.sin(0.5);

				var arrGap = (calcStrWidth(d, edgeScale) * markerSide * 10/16);
				var x2 = layout[d.from][0] + node_radius * Math.cos(0.5); 
				var y2 = layout[d.from][1] - node_radius * Math.sin(0.5); 
				if (!d.occurrences) {
					x2 += arrGap;
					y2 -= arrGap;
				}

				var drx = node_radius;
				var dry = node_radius;

				var xrot = 0;

				var largeArcFlag = 1;
				var sweepFlag = 0;

				return 'M' + x1 + ' ' + y1 + ' A' + drx + ' ' + dry + ', ' + xrot + ',' + largeArcFlag + ', ' + sweepFlag + ', ' + x2 + ' ' + y2;	
			}
		})
		.transition()
		.duration(transition_duration )
		.delay(edge_delay)
		.attrTween('d', function(d, i) {
			return circlePathInterp(d3.select(this).node(), layout, node_radius)(d, i);
		}) 
		.attr('opacity', 1);

		paths.select('title')
			.text(function(d, i) {
			    return 'Edge = (' + d.from + ', ' + d.to + ')';
			});
}

var drawSelfEdges = function(svg, edges, layout, node_radius, edgeScale) {
	var doneEdges = svg.selectAll('path.edge')
		.data(edges)
		.exit()
		.transition()
		.duration(transition_duration)
		.remove();

	var newEdges = svg.selectAll('path.edge')
		.data(edges)
		.enter()
		.append('path')
		.attr('class', 'edge')
		.attr('stroke-linecap', 'round')
		.attr('opacity', 0)
		.attr('stroke', 'black')
		.attr('stroke-width', 4)
		.attr('marker-end', function(d) {
			if (!d.occurrences){
				return 'url(#arrow-head)';
			}
		})
		.attr('fill', 'transparent');

	newEdges.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d.from + ', ' + d.to + ')';
	    });

	var allEdges = svg.selectAll('path.edge');

	updateSelfEdges(allEdges, layout, node_radius, edgeScale);
}

var update_nodes = function(nodes, layout) {
	nodes.transition()
	.duration(transition_duration)
	.attr('cx', function(d, i) {
        return layout[i][0];
    })
    .attr('cy', function(d, i) {
        return layout[i][1];
    })
    .attr('fill-opacity', 1)
    .attr('fill', cur_color);
	 
    nodes.select('title')
    	.text(function(d, i) {
    		        return 'Node ' + d.id;
    	});
}

var draw_nodes = function(svg, node_lst, layout, node_radius) {
	// Grab nodes that need to vanish and update
	var done_nodes = svg.selectAll('circle.node')
		.data(node_lst)
		.exit()
		.transition()
		.duration(transition_duration)
		.attr('cx', svgWidth(svg)/2)
	    .attr('cy', svgHeight(svg)/2)
	    .attr('fill-opacity', 0)
		.remove();

	// Create new nodes
	var new_nodes = svg.selectAll('circle.node')
	    .data(node_lst)
	    .enter()
	    .append('circle')
	    .attr('class', 'node')
	    .attr('r', node_radius)
	    .attr('fill', 'teal')
	    .attr('cx', svgWidth(svg)/2)
	    .attr('cy', svgHeight(svg)/2)
	    .attr('fill-opacity', 0);

	new_nodes.append('title')
	    .text(function(d, i) {
	        return 'Node ' + d.id;
	    });

	// Grab all nodes and update
	var cur_nodes = svg.selectAll('circle.node')
	    .data(node_lst);
	update_nodes(cur_nodes, layout);
	

}

var draw_graph = function(svg, node_lst, edges, layout, node_radius, edgeScale) {
	if (arrowHead == null) {
		initArrowHead(svg);
	}

	if (!edgeScale) {
		edgeScale = d3.scaleLinear();
	}

	//randColor();
	nextColor();

	lineEdges = edges.filter(e => e.from != e.to);
	selfEdges = edges.filter(e => e.from == e.to);

	drawLineEdges(svg, lineEdges, layout, node_radius, edgeScale);
	drawSelfEdges(svg, selfEdges, layout, node_radius, edgeScale);

	draw_edge_hovers(svg, lineEdges, layout, node_radius, edgeScale);
	drawSelfEdgeHovers(svg, selfEdges, layout, node_radius, edgeScale);

	draw_nodes(svg, node_lst, layout, node_radius);
}


var padLayoutsSquare = function(svg, layout) {
	var whalf = svgWidth(svg)/2;
	var hhalf = svgHeight(svg)/2;
	var side = Math.min(whalf, hhalf);
	var nrad = rad5(svg);
	var pad = nrad * 3;

	var padded = layout.map(function(coords) {
		var x = coords[0];
		var y = coords[1];
		var nx = x * (side - pad) + whalf;
		var ny = y * (side - pad) + hhalf;
		return [nx, ny];
	});

	return padded;
}

var drawGraphPadded = function(svg, node_lst, edge_lst, layout_lst) {
	var padLay = padLayoutsSquare(svg, layout_lst);
	var nrad = rad5(svg);
	draw_graph(svg, node_lst, edge_lst, padLay, nrad);
}

var nodeOnClick = function(f) {
	d3.selectAll('circle.node')
		.on('click', f);
}

var edgeOnClick = function(f) {
	d3.selectAll('line.edge-hover, line.edge')
		.on('click', f);
}

var nodeInfo = function(n) {
	console.log('n = ' + n);
}

var edgeInfo = function(e) {
	console.log('e = ' + e);
}



