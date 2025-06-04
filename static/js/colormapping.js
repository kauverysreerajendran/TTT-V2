document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('#order-listing tbody tr').forEach(function(row) {
    var cell = row.children[3];
    if (!cell) return;
    var colorText = (cell.textContent || "").trim().toLowerCase();
    if (!colorText || colorText === "n/a") return;

      var colorMap = {
    "black": { bg: "linear-gradient(135deg, #222 60%, #555 100%)", border: "#888" },      "white":   { bg: "linear-gradient(135deg, #fff 60%, #eaeaea 100%)", border: "#000" },
      "rose":    { bg: "linear-gradient(135deg, #e3a6a1 60%, #f7cac9 100%)", border: "#b76e79" },
      "yellow":  { bg: "linear-gradient(135deg, #ffe066 60%, #fffbe6 100%)", border: "#bfa600" },
      "gold":    { bg: "linear-gradient(135deg, #ffd700 60%, #fffbe6 100%)", border: "#bfa600" },
      "silver":  { bg: "linear-gradient(135deg, #c0c0c0 60%, #f5f5f5 100%)", border: "#888" },
      "blue":    { bg: "linear-gradient(135deg, #0074d9 60%, #7fdbff 100%)", border: "#fff" },
      "green":   { bg: "linear-gradient(135deg, #2ecc40 60%, #b6fcd5 100%)", border: "#fff" },
      "brown":   { bg: "linear-gradient(135deg, #b97a56 60%, #ffe066 100%)", border: "#8d5524" },
      "ip-brown":{ bg: "linear-gradient(135deg, #b97a56 60%, #ffe066 100%)", border: "#8d5524" }
    };

    var match = Object.keys(colorMap).find(function(key) {
      return colorText.includes(key);
    });

    // Remove any previous indicator
    var oldCircle = cell.querySelector('.plating-color-indicator');
    if (oldCircle) oldCircle.remove();

        if (match) {
      var style = colorMap[match];
      var circle = document.createElement('span');
      circle.className = 'plating-color-indicator';
      circle.style.display = 'inline-block';
      circle.style.width = '16px';
      circle.style.height = '16px';
      circle.style.borderRadius = '50%';
      circle.style.marginRight = '6px';
      circle.style.verticalAlign = 'middle';
      // Support gradient backgrounds
      if (style.bg.startsWith("linear-gradient")) {
        circle.style.background = "";
        circle.style.backgroundImage = style.bg;
      } else {
        circle.style.background = style.bg;
      }
      circle.style.border = '2px solid ' + style.border;
      cell.insertBefore(circle, cell.firstChild);
    }
  });
});