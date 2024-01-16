//js
function initGraphInteractions(graphDiv) {
    graphDiv.onmousedown = function (event) {
        if (event.target.classList.contains('yaxislayer')) {
            const startY = event.clientY;
            const startHeight = graphDiv.clientHeight;

            document.onmousemove = function (event) {
                const deltaY = event.clientY - startY;
                const newHeight = Math.max(100, startHeight + deltaY);
                graphDiv.style.height = newHeight + 'px';
                Plotly.Plots.resize(graphDiv);
            };

            document.onmouseup = function () {
                document.onmousemove = document.onmouseup = null;
            };
        }
    };
}

document.addEventListener('DOMContentLoaded', function () {
    var checkExist = setInterval(function () {
        const graphDiv = document.getElementById('currency-pair-graph');
        if (graphDiv) {
            initGraphInteractions(graphDiv);
            clearInterval(checkExist);
        }
    }, 100); // Проверяем каждые 100 мс
});
