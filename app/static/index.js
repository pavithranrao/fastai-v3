var canvas = document.getElementById('paint');
var ctx = canvas.getContext('2d');

canvas.width = 280;
canvas.height = 280;
var mouse = {x: 0, y: 0};
var predictPressed = false;

/* Mouse Capturing Work */
canvas.addEventListener('mousemove', function (e) {
    mouse.x = e.pageX - this.offsetLeft;
    mouse.y = e.pageY - this.offsetTop;
}, false);

/* Drawing on Paint App */
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.lineWidth = 20;
ctx.strokeStyle = "white";


function predict() {
    predictPressed = true;
    var data = canvas.toDataURL();
    var output = data.replace(/^data:image\/(png|jpg);base64,/, "");
    $.post("/analyze", {
        javascript_data: output
    }, function (data) {
        document.getElementById("result").innerHTML = data["result"];
    });
}

function reset() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}


canvas.addEventListener('mousedown', function (e) {
    if (predictPressed) {
        reset();
        predictPressed = false;
    }
    ctx.beginPath();
    ctx.moveTo(mouse.x, mouse.y);

    canvas.addEventListener('mousemove', onPaint, false);
}, false);

canvas.addEventListener('mouseup', function () {
    canvas.removeEventListener('mousemove', onPaint, false);
}, false);

var onPaint = function () {
    ctx.lineTo(mouse.x, mouse.y);
    ctx.stroke();
};