var options = {
physics: {
barnesHut: {
gravitationalConstant: -36,
centralGravity: 0.005,
springLength: 230,
springConstant: 0.18
},
maxVelocity: 146,
solver: 'forceAtlas2Based',
timestep: 0.35,
stabilization: {
enabled:true,
iterations:2000,
updateInterval:25
}
},
interaction:{hover:true},
edges:{smooth: false}
};

var nodes = [
{id: 1, label: 'A47', value: 1},
{id: 2, label: 'A78', value: 1},
{id: 3, label: 'A89', value: 1},
{id: 4, label: 'D103', value: 1},
{id: 5, label: 'D186', value: 1},
{id: 6, label: 'D187', value: 1},
{id: 7, label: 'D61', value: 2},
{id: 8, label: 'E81', value: 1},
{id: 9, label: 'G252', value: 1},
{id: 10, label: 'G62', value: 1},
{id: 11, label: 'G65', value: 5},
{id: 12, label: 'G91', value: 1},
{id: 13, label: 'L68', value: 1},
{id: 14, label: 'L77', value: 1},
{id: 15, label: 'N110', value: 1},
{id: 16, label: 'N158', value: 1},
{id: 17, label: 'N85', value: 1},
{id: 18, label: 'N94', value: 1},
{id: 19, label: 'S111', value: 1},
{id: 20, label: 'S67', value: 3},
{id: 21, label: 'V201', value: 3},
{id: 22, label: 'W234', value: 2}];

var edges = [
{from: 1, to: 2, color:{color:'green'}, title: 5},
{from: 7, to: 20, color:{color:'green'}, title: 13},
{from: 7, to: 21, color:{color:'green'}, title: 16},
{from: 10, to: 11, color:{color:'green'}, title: 12},
{from: 11, to: 20, color:{color:'green'}, title: 16},
{from: 11, to: 19, color:{color:'green'}, title: 7},
{from: 11, to: 21, color:{color:'green'}, title: 20},
{from: 11, to: 9, color:{color:'green'}, title: 9},
{from: 20, to: 21, color:{color:'green'}, title: 19},
{from: 13, to: 16, color:{color:'green'}, title: 7},
{from: 14, to: 22, color:{color:'green'}, title: 8},
{from: 8, to: 4, color:{color:'green'}, title: 5},
{from: 17, to: 3, color:{color:'green'}, title: 5},
{from: 12, to: 18, color:{color:'green'}, title: 20},
{from: 15, to: 22, color:{color:'green'}, title: 6},
{from: 5, to: 6, color:{color:'green'}, title: 20},
];
