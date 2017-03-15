var transition_duration = 700;
var edge_duration = transition_duration/2;
var edge_delay = transition_duration / 2;
var hover_width = 15;
var allColors = d3.schemeCategory10;
var curColorPos = 0;
var cur_color = 'teal';
var markerSide = 4;
var allInteractionColors = ['#000', 
							'#e41a1c', 
							"#377eb8", 
							"#4daf4a", 
							"#984ea3",
							"#ff7f00",
							"#ffff33",
							"#a65628",
							"#f781bf",
							"#999999"]

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

var getInteractionColor = function(i) {
	if (!i) {
		i = 0;
	} 
	return allInteractionColors[i % allInteractionColors.length]; 
}

var highlight = function(item) {
	item.attr('stroke-opacity', 0.5);
}



// Define arrow endings for edges
var arrowHeads = null;
    
var initArrowHeads = function(svg) {
	var g = svg.append('g')
		.attr('id', 'marker-g');

	for (var i = 1; i <= allInteractionColors.length; i++) {
		var arrowHead = g.append('marker')
		    .attr('id', 'arrow-head-' + i)
		    .attr('orient', 'auto')
		    .attr('refX', 0.1)
		    .attr('refY', 2)
		    .attr('markerWidth', 4)
		    .attr('markerHeight', 4);

		arrowHead.append('path')
		    .attr('d', 'M 0 0 V ' + markerSide +'L ' + markerSide + ' ' + markerSide/2 + ' Z')
		    .attr('fill', getInteractionColor(i-1));
	}

	var complexArrow = g.append('marker')
	    .attr('id', 'arrow-head-complex')
	    .attr('orient', 'auto')
	    .attr('refX', 0.1)
	    .attr('refY', 2)
	    .attr('markerWidth', 4)
	    .attr('markerHeight', 4);

	complexArrow.append('path')
	    .attr('d', 'M 0 0 V ' + markerSide +'L ' + markerSide + ' ' + markerSide/2 + ' Z')
	    .attr('fill', '#ccc');
	arrowHeads = true;
}

var getArrowHead = function(ee) {
	if (ee.complex) {
		return 'url(#arrow-head-complex)';
	}
	else {
		var inter = ee.interaction;
		if (!inter) {
			inter = 0;
		}
		return 'url(#arrow-head-' + (inter+1) + ')'
	}
	
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

var calcStrWidth = function(svg, d, edgeScale) {
	occ = d.occurrences;
	if (!occ) {
		occ = 4;
	}
	var strScale = edgeScale(occ)/500;
	var minSide = Math.min(svgWidth(svg), svgHeight(svg));
	var strWidth = minSide * strScale;
	return strWidth;
}

var update_edge_hovers = function(svg, lines, layout, node_radius, edgeScale, color) {
	lines.transition()
    .duration(transition_duration/4)
    .attr('stroke', color)
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
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[1][1];
	})
    .attr('stroke-width', d => calcStrWidth(svg, d, edgeScale) + 10);

    lines.select('title')
    	.text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });
}

var updateLineEdges = function(svg, lines, layout, node_radius, edgeScale) {

	lines.transition()
	.duration(transition_duration/4)
	.attr('opacity', 0)
	.attr('stroke-width', function(d) {
		return calcStrWidth(svg, d, edgeScale);
	})
	.attr('marker-end', e => getArrowHead(e))
	.attr('stroke', function(e) {
		if (e.complex) {
			return '#ccc';
		}
		else {
			return getInteractionColor(e.interaction);
		}
	})
	.transition()
	.duration(0)
	.attr('x1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][1];
	})
	.transition()
	.duration(edge_duration)
	.delay(edge_delay)
	.attr('x1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d.from];
	    var n2 = layout[d.to];
	    pos = line_shorten(n1, n2, node_radius, calcStrWidth(svg, d, edgeScale));
	    return pos[1][1];
	})
	.attr('opacity', function(e) {
		if (e.complex) {
			return 0.5;
		}
		else {
			return 1;
		}
	});

	lines.select('title')
		.text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });
}


var draw_edge_hovers = function(svg, edges, layout, node_radius, edgeScale, color) {
	if (! $('#edge-hover-g').length) {
		svg.append('g')
			.attr('id', 'edge-hover-g');
	}

	// Grab edge-hovers that need to vanish and update
	var done_edge_hovers = svg.select('#edge-hover-g')
		.selectAll('line.edge-hover')
		.data(edges)
		.exit()
		.remove();

	// Create new edge hovers 
	var new_edge_hovers = svg.select('#edge-hover-g')
		.selectAll('line.edge-hover')
		.data(edges)
		.enter()
	    .append('line')
		.attr('class', 'edge-hover')
	    .attr('stroke', color)
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
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });

	// Grab existing edge hovers and update
	var all_hovers = svg.select('#edge-hover-g')
		.selectAll('line.edge-hover')
		.data(edges);
	update_edge_hovers(svg, all_hovers, layout, node_radius, edgeScale, color);
}


var drawLineEdges = function(svg, edges, layout, node_radius, edgeScale) {
	if (! $('#edge-g').length) {
		svg.append('g')
			.attr('id', 'edge-g');
	}

	if (arrowHeads == null) {
		initArrowHeads(svg);
	}

	// Grab edges that need to vanish and update
	var done_edges = svg.select('#edge-g')
		.selectAll('line.edge')
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
	var new_edges = svg.select('#edge-g')
		.selectAll('line.edge')
		.data(edges)
		.enter()
		.append('line')
		.attr('class', 'edge')
	    .attr('stroke-width', function(d) {
	    	return calcStrWidth(svg, d, edgeScale);
	    })
	    .attr('x1', svgWidth(svg)/2)
	    .attr('y1', svgHeight(svg)/2)
	    .attr('x2', svgWidth(svg)/2)
	    .attr('y2', svgHeight(svg)/2)
	    .attr('opacity', 0);

	new_edges.append('title')
	    .text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });

	// Grab all edges
	var all_edges = svg.select('#edge-g')
		.selectAll('line.edge')
		.data(edges);

	updateLineEdges(svg, all_edges, layout, node_radius, edgeScale);

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

var updateSelfEdgeHovers = function(svg, paths, layout, node_radius, edgeScale, color) {
	var numNodes = layout.length;
	var step = 360 / numNodes;
	paths.attr('stroke', color)
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

				var arrGap = (calcStrWidth(svg, d, edgeScale) * markerSide * 10/16);
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
		.attr('stroke-width', d => calcStrWidth(svg, d, edgeScale) + 10);

	paths.select('title')
		.text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });
}



var drawSelfEdgeHovers = function(svg, edges, layout, node_radius, edgeScale, color) {
	if (! $('#self-edge-hover-g').length) {
		svg.append('g')
			.attr('id', 'self-edge-hover-g');
	}

	// Grab edge-hovers that need to vanish and update
	var done_edge_hovers = svg.select('#self-edge-hover-g')
		.selectAll('path.edge-hover')
		.data(edges)
		.exit()
		.remove();

	// Create new edge hovers 
	var new_edge_hovers = svg.select('#self-edge-hover-g')
		.selectAll('path.edge-hover')
		.data(edges)
		.enter()
	    .append('path')
		.attr('class', 'edge-hover')
	    .attr('stroke', color)
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
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });

	// Grab existing edge hovers and update
	var all_hovers = svg.select('#self-edge-hover-g')
		.selectAll('path.edge-hover')
		.data(edges);

	updateSelfEdgeHovers(svg, all_hovers, layout, node_radius, edgeScale, color);
}

var updateSelfEdges = function(svg, paths, layout, node_radius, edgeScale) {
	var numNodes = layout.length;
	var step = 360 / numNodes;
	paths.attr('opacity', 0)
		.attr('stroke-width', d => calcStrWidth(svg, d, edgeScale))		
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

				var arrGap = (calcStrWidth(svg, d, edgeScale) * markerSide * 10/16);
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
		.attr('marker-end', function(d) {
			if (!d.occurrences){
				return getArrowHead(d);
			}
		})
		.attr('stroke', function(e) {
			if (e.complex) {
				return '#ccc';
			}
			else {
				return getInteractionColor(e.interaction);
			}
		})
		.transition()
		.duration(transition_duration )
		.delay(edge_delay)
		.attrTween('d', function(d, i) {
			return circlePathInterp(d3.select(this).node(), layout, node_radius)(d, i);
		}) 
		.attr('opacity', e => e.complex ? 0.5 : 1);

		paths.select('title')
			.text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });
}

var drawSelfEdges = function(svg, edges, layout, node_radius, edgeScale) {
	if (! $('#self-edge-g').length) {
		svg.append('g')
			.attr('id', 'self-edge-g');
	}

	var doneEdges = svg.select('#self-edge-g')
		.selectAll('path.edge')
		.data(edges)
		.exit()
		.remove();

	var newEdges = svg.select('#self-edge-g')
		.selectAll('path.edge')
		.data(edges)
		.enter()
		.append('path')
		.attr('class', 'edge')
		.attr('stroke-linecap', 'round')
		.attr('opacity', 0)
		.attr('stroke-width', 4)
		.attr('fill', 'transparent');

	newEdges.append('title')
	    .text(function(d, i) {
    		var from = d.from;
    		var to = d.to
    		if (d.interactome) {
    			from = '[' + d.interactome + ']';
    		}
    		else if (d.complex) {
    			from = '[' + d.complex + ']';
    			to = d.complexTo;
    		}
            return 'Edge = (' + from + ', ' + to + ')';
        });

	var allEdges = svg.select('#self-edge-g')
		.selectAll('path.edge');

	updateSelfEdges(svg, allEdges, layout, node_radius, edgeScale);
}

var update_nodes = function(nodes, layout, color) {
	nodes.transition()
	.duration(transition_duration)
	.attr('cx', function(d, i) {
        return layout[i][0];
    })
    .attr('cy', function(d, i) {
        return layout[i][1];
    })
    .attr('fill-opacity', 1)
    .attr('fill', function(d) {
    	if (d.complex) {
    		return '#ccc'
    	}
    	else {
    		return color;
    	}
    });
	 
    nodes.select('title')
    	.text(function(d, i) {
    		if (d.complex) {
    			return 'Node [' + d.complex + ']';
    		}
    		else {
			    return 'Node ' + d.id;
    		}
    		    
    	});
}

var draw_nodes = function(svg, node_lst, layout, node_radius, color) {
	if (! $('#node-g').length) {
		svg.append('g')
			.attr('id', 'node-g');
	}

	// Grab nodes that need to vanish and update
	var done_nodes = svg.select('#node-g')
		.selectAll('circle.node')
		.data(node_lst)
		.exit()
		.transition()
		.duration(transition_duration)
		.attr('cx', svgWidth(svg)/2)
	    .attr('cy', svgHeight(svg)/2)
	    .attr('fill-opacity', 0)
		.remove();

	// Create new nodes
	var new_nodes = svg.select('#node-g')
		.selectAll('circle.node')
	    .data(node_lst)
	    .enter()
	    .append('circle')
	    .attr('class', 'node')
	    .attr('r', function(d) {
	    	if (d.complex) {
	    		return node_radius / 2;
	    	}
	    	else {
	    		return node_radius;
	    	}
	    })
	    .attr('fill', 'teal')
	    .attr('cx', svgWidth(svg)/2)
	    .attr('cy', svgHeight(svg)/2)
	    .attr('fill-opacity', 0);

	new_nodes.append('title')
	    .text(function(d, i) {
	    	if (d.complex) {
	    		return 'Node [' + d.complex + ']';
	    	}
	    	else {
	    		return 'Node ' + d.id;
	    	}  
	    });

	// Grab all nodes and update
	var cur_nodes = svg.select('#node-g')
		.selectAll('circle.node')
	    .data(node_lst);

	update_nodes(cur_nodes, layout, color);
}

var draw_graph_color = function(svg, node_lst, edges, layout, node_radius, color, edgeScale) {
	if (arrowHeads == null) {
		initArrowHeads(svg);
	}

	if (!edgeScale) {
		edgeScale = d3.scaleLinear();
	}

	

	lineEdges = edges.filter(e => e.from != e.to);
	selfEdges = edges.filter(e => e.from == e.to);

	drawLineEdges(svg, lineEdges, layout, node_radius, edgeScale);
	drawSelfEdges(svg, selfEdges, layout, node_radius, edgeScale);

	draw_edge_hovers(svg, lineEdges, layout, node_radius, edgeScale, color);
	drawSelfEdgeHovers(svg, selfEdges, layout, node_radius, edgeScale, color);

	draw_nodes(svg, node_lst, layout, node_radius, color);
}

var draw_graph = function(svg, node_lst, edges, layout, node_radius, edgeScale) {
	nextColor();
	draw_graph_color(svg, node_lst, edges, layout, node_radius, cur_color, edgeScale)

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

var drawGraphPadded = function(svg, node_lst, edge_lst, layout_lst, edgeScale) {
	var processed = preprocess(node_lst, edge_lst)
	nodes = processed[0];
	edges = processed[1];
	layout = processed[2];
	var padLay = padLayoutsSquare(svg, layout);
	var nrad = rad5(svg);
	draw_graph(svg, nodes, edges, padLay, nrad, edgeScale);
}

var drawGraphPaddedColor = function(svg, node_lst, edge_lst, layout_lst, color, edgeScale) {
	var processed = preprocess(node_lst, edge_lst)
	nodes = processed[0];
	edges = processed[1];
	layout = processed[2];
	var padLay = padLayoutsSquare(svg, layout);
	var nrad = rad5(svg);
	draw_graph_color(svg, nodes, edges, padLay, nrad, color, edgeScale);
}

var nodeOnClick = function(f) {
	d3.selectAll('circle.node')
		.on('click', null)
		.on('click', f);
}

var edgeOnClick = function(f) {
	d3.selectAll('.edge-hover, .edge')
		.on('click', null)
		.on('click', f);
}

var nodeInfo = function(n) {
	console.log('n = ' + n);
}

var edgeInfo = function(e) {
	console.log('e = ' + e);
}


var circleLayout = function(nodes) {
	var step = Math.PI * 2 / nodes.length;
	var layout = [];
	for (var i = 0; i < nodes.length; i++) {
		var theta = step * i;
		var x = Math.cos(theta);
		var y = Math.sin(theta);
		layout.push([x,y]);
	}
	return layout;
}


var preprocess = function(nodes, edges) {
	maxIdx = nodes.map(n => n.id).reduce((a, b) => Math.max(a,b)) + 1;
	complexNodes = nodes.concat([])
	newEdges = []
	for (var i = 0; i < edges.length; i++) {
		e = edges[i];
		if (e.from.length && e.from.length > 1) {
			// Add complex Node
			complexNodes.push({
				id: maxIdx,
				complex: e.from,
				parameters: []
			});

			// Add edges to complex node
			e.from.forEach(function(n) {
				newEdges.push({
					from: n,
					to: maxIdx,
					parameters: [],
					interaction: e.interaction,
					complex: e.from,
					complexTo: e.to
				})
			})

			// Add edge from complex node
			newEdges.push({
				from: maxIdx,
				to: e.to,
				parameters: e.parameters,
				interaction: e.interaction,
				interactome: e.from
			})
			maxIdx += 1;
		} 
		else {
			newEdges.push(e);
		}
	}

	newLayouts = circleLayout(complexNodes);
	return [complexNodes, newEdges, newLayouts];
}